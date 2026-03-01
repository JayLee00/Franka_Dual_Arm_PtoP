#!/usr/bin/env python3
"""
BC 모델 진단 스크립트

1. 정규화 통계 (action mean/std) 출력
2. 학습 데이터에서 샘플 뽑아 모델 예측 vs 정답 비교 (훈련셋 재현성 확인)
3. 관절별 예측 오차 리포트
4. 핸드가 안 움직이거나 이상하게 움직이는 원인 파악

실행:
  python3 bc_check.py \
      --model     ./bc_model/bc_best.pt \
      --state_norm  ./bc_model/state_norm.npz \
      --action_norm ./bc_model/action_norm.npz \
      --data_dir  ./HDF5
"""

import argparse
import glob
import os
import sys

import h5py
import numpy as np
import torch
import torch.nn as nn

TACTILE_THRESH     = 1000
FINGERS            = 4
TACTILE_PER_FINGER = 15
STATE_DIM          = 32
ACTION_DIM         = 16

JOINT_NAMES = [
    "J0 ", "J1 ", "ThumbMCP", "ThumbPIP", "ThumbDIP",
    "IdxMCP", "IdxPIP ", "IdxDIP ",
    "J8 ", "MidMCP", "MidPIP ", "MidDIP ",
    "J12", "J13", "J14", "J15",
]
JOINT_LIMITS = [(-1000,1000) if i in (4,8,12) else (-4096,4096) if i==1 else (0,4096)
                for i in range(16)]


# ── 모델 (bc_run.py와 동일) ────────────────────────────────────────────────────
class BCMLP(nn.Module):
    def __init__(self, state_dim=STATE_DIM, action_dim=ACTION_DIM, hidden=256, dropout=0.0):
        super().__init__()
        def block(a, b):
            return nn.Sequential(nn.Linear(a,b), nn.LayerNorm(b), nn.ReLU(), nn.Dropout(dropout))
        self.net = nn.Sequential(block(state_dim,hidden), block(hidden,hidden),
                                 block(hidden,hidden), nn.Linear(hidden,action_dim))
    def forward(self, x): return self.net(x)


# ── 데이터 로드 (bc_train.py와 동일) ─────────────────────────────────────────
def load_samples(data_dir: str, max_demos: int = 20):
    """HDF5에서 최대 max_demos개 demo 로드 → (states, actions) numpy array"""
    files = sorted(glob.glob(os.path.join(data_dir, '**', '*.hdf5'), recursive=True))
    if not files:
        print(f"[ERROR] {data_dir} 에 HDF5 파일 없음")
        sys.exit(1)

    states_list, actions_list = [], []
    demo_cnt = 0
    for path in files:
        with h5py.File(path, 'r') as f:
            root = f.get('data', f)
            for key in sorted(root.keys()):
                if not key.startswith('demo_'):
                    continue
                d = root[key]
                if not {'Real_hand_joint_pos','Real_hand_kinesthetic',
                        'Real_hand_tactile','Real_hand_target'}.issubset(d.keys()):
                    continue
                jp  = d['Real_hand_joint_pos'][:].astype(np.float32)
                kin = d['Real_hand_kinesthetic'][:].astype(np.float32)
                tac = d['Real_hand_tactile'][:]
                tgt = d['Real_hand_target'][:].astype(np.float32)
                N = jp.shape[0]
                tac4 = (tac.reshape(N, FINGERS, TACTILE_PER_FINGER).max(axis=2)
                        > TACTILE_THRESH).astype(np.float32)
                states_list.append(np.concatenate([jp, kin, tac4], axis=1))
                actions_list.append(tgt)
                demo_cnt += 1
                if demo_cnt >= max_demos:
                    break
        if demo_cnt >= max_demos:
            break

    print(f"[DATA] {demo_cnt} demos 로드 ({sum(s.shape[0] for s in states_list):,} samples)")
    return np.concatenate(states_list), np.concatenate(actions_list)


def main():
    parser = argparse.ArgumentParser(description='BC 진단 스크립트')
    parser.add_argument('--model',       default='./bc_model/bc_best.pt')
    parser.add_argument('--state_norm',  default='./bc_model/state_norm.npz')
    parser.add_argument('--action_norm', default='./bc_model/action_norm.npz')
    parser.add_argument('--data_dir',    default='./HDF5')
    parser.add_argument('--n_samples',   type=int, default=500, help='평가할 샘플 수')
    args = parser.parse_args()

    # ── 로드 ──────────────────────────────────────────────────────────────────
    ckpt = torch.load(args.model, map_location='cpu', weights_only=True)
    model = BCMLP(hidden=ckpt.get('hidden', 256))
    model.load_state_dict(ckpt['model_state'])
    model.eval()
    print(f"[MODEL] epoch={ckpt.get('epoch','?')}  val_loss={ckpt.get('val_loss',0):.5f}")

    s_d = np.load(args.state_norm)
    s_mean, s_std = s_d['mean'], s_d['std']
    a_d = np.load(args.action_norm)
    a_mean, a_std = a_d['mean'], a_d['std']

    # ── 1. 정규화 통계 ─────────────────────────────────────────────────────────
    print("\n" + "="*65)
    print("■ ACTION 정규화 통계 (학습 데이터의 target 분포)")
    print(f"  {'Joint':<12}  {'mean':>8}  {'std':>8}  {'min가능':>10}  {'max가능':>10}")
    print("-"*65)
    for i in range(ACTION_DIM):
        lo, hi = JOINT_LIMITS[i]
        print(f"  {JOINT_NAMES[i]:<12}  {a_mean[i]:>8.1f}  {a_std[i]:>8.1f}"
              f"  {lo:>10}  {hi:>10}")
    print()
    small_std = [i for i in range(ACTION_DIM) if a_std[i] < 30]
    if small_std:
        print(f"  ⚠ std < 30 인 관절: {[JOINT_NAMES[i].strip() for i in small_std]}")
        print(f"    → 학습 데이터에서 이 관절들의 변화가 거의 없었음 (모델이 학습하기 어려움)")

    # ── 2. 학습 샘플에서 예측 정확도 ──────────────────────────────────────────
    print("\n" + "="*65)
    print("■ 학습 데이터 재현성 검증 (모델이 학습 데이터를 제대로 학습했는지)")

    states, actions = load_samples(args.data_dir, max_demos=50)
    idx = np.random.choice(len(states), min(args.n_samples, len(states)), replace=False)
    S = states[idx]
    A = actions[idx]

    # 정규화 후 예측
    S_norm = (S - s_mean) / s_std
    with torch.no_grad():
        pred_norm = model(torch.from_numpy(S_norm.astype(np.float32))).numpy()
    pred = pred_norm * a_std + a_mean   # denormalize

    err = np.abs(pred - A)   # (N, 16)
    print(f"\n  {'Joint':<12}  {'MAE':>8}  {'actual_std':>12}  {'판정':>6}")
    print("-"*55)
    for i in range(ACTION_DIM):
        mae   = err[:, i].mean()
        a_s   = A[:, i].std()
        ratio = mae / (a_s + 1e-6)
        status = "OK" if ratio < 0.5 else ("△" if ratio < 1.0 else "✗")
        print(f"  {JOINT_NAMES[i]:<12}  {mae:>8.1f}  {a_s:>12.1f}  {status:>6}")

    total_mae = err.mean()
    print(f"\n  전체 평균 MAE : {total_mae:.2f}")

    # ── 3. 모델 붕괴(collapse) 체크 ───────────────────────────────────────────
    print("\n" + "="*65)
    print("■ 모델 출력 다양성 (collapse 여부)")
    pred_std = pred.std(axis=0)
    print(f"  {'Joint':<12}  {'pred_std':>10}  {'target_std':>12}  {'비율':>8}")
    print("-"*55)
    for i in range(ACTION_DIM):
        ratio = pred_std[i] / (A[:,i].std() + 1e-6)
        flag = " ← collapse!" if ratio < 0.1 else ""
        print(f"  {JOINT_NAMES[i]:<12}  {pred_std[i]:>10.1f}  {A[:,i].std():>12.1f}"
              f"  {ratio:>8.2f}{flag}")

    collapsed = [i for i in range(ACTION_DIM) if pred_std[i] < 0.1 * (A[:,i].std()+1e-6)]
    if collapsed:
        print(f"\n  ⚠ COLLAPSE 의심 관절: {[JOINT_NAMES[i].strip() for i in collapsed]}")
        print(f"    → 이 관절들은 상태와 무관하게 항상 같은 값을 출력 중")
    else:
        print(f"\n  ✓ 모델 출력 다양성 정상")

    # ── 4. 현재 state vs 학습 state 분포 비교 ─────────────────────────────────
    print("\n" + "="*65)
    print("■ 학습 state 분포 (추론 시 현재 state와 비교용)")
    state_std = states.std(axis=0)
    state_mean_v = states.mean(axis=0)
    print(f"  joint_pos  mean : [{', '.join(f'{v:.0f}' for v in state_mean_v[:6])} ...]")
    print(f"  joint_pos  std  : [{', '.join(f'{v:.0f}' for v in state_std[:6])} ...]")
    print(f"  kinesthetic mean: [{', '.join(f'{v:.0f}' for v in state_mean_v[16:22])} ...]")
    print(f"  tactile contact % : "
          f"{states[:, 28:32].mean(axis=0) * 100}")

    print("\n  → 추론 시 현재 핸드 관절값이 위 mean±2*std 범위 안에 있어야 정상 예측 가능")
    print("    (범위 밖이면 covariate shift — 학습 데이터와 시작 자세가 다른 것)")

    print("\n" + "="*65)
    print("■ 요약")
    if total_mae > 200:
        print(f"  ✗ MAE={total_mae:.0f} 높음 → 모델이 학습 데이터도 제대로 재현 못 함")
        print(f"    원인: 데이터 부족 / 학습 부족 / 데이터 품질 문제")
    elif collapsed:
        print(f"  △ MAE 낮지만 일부 관절 collapse → 더 많은 데이터 필요")
    else:
        print(f"  ✓ MAE={total_mae:.0f} 학습 데이터 재현 OK")
        print(f"    → 추론 시 핸드 초기 자세가 학습 데이터와 달라서 covariate shift 발생 가능")
        print(f"    해결: 추론 전에 핸드를 학습 시작 자세(mean 부근)로 초기화 후 실행")


if __name__ == '__main__':
    main()
