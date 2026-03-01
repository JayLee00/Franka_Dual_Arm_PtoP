#!/usr/bin/env python3
"""
BC (Behavioral Cloning) 학습 스크립트 — KISTAR Hand 전구 돌리기 태스크

입력 state (32차원):
  - Real_hand_joint_pos    (16,) : 현재 핸드 관절 위치  [int16 → float32]
  - Real_hand_kinesthetic  (12,) : 역감 센서             [int16 → float32]
  - tactile_contact         (4,) : 손가락별 접촉 binary  [60 → 4×15 max > THRESH]

출력 action (16차원):
  - Real_hand_target        (16,) : 글러브 기반 목표 관절 위치

네트워크: MLP 32→256→256→256→16  (LayerNorm + ReLU + Dropout)
손실함수: MSELoss
최적화:   Adam (weight_decay=1e-4) + CosineAnnealingLR
추가:     Gradient clipping (max_norm=1.0) + Early stopping

실행 예시:
  python3 bc_train.py --data_dir ./HDF5 --out_dir ./bc_model --epochs 300

파일 출력:
  bc_model/bc_best.pt        ← 학습된 모델
  bc_model/state_norm.npz    ← state z-score 정규화 파라미터
  bc_model/action_norm.npz   ← action z-score 정규화 파라미터
"""

import argparse
import glob
import os
import time

import h5py
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, random_split

# ── 상수 ──────────────────────────────────────────────────────────────────────
TACTILE_THRESH      = 1000   # 접촉 판별 임계값 (int16 raw)
FINGERS             = 4      # 손가락 수
TACTILE_PER_FINGER  = 15     # 손가락당 촉각 센서 수 (60 / 4)
STATE_DIM           = 16 + 12 + 4   # 32
ACTION_DIM          = 16


def _open_h5_read(path: str, max_retries: int = 5, retry_delay: float = 0.5):
    """다른 프로세스가 파일을 사용 중일 수 있을 때 재시도하며 HDF5 읽기용으로 연다."""
    last_err = None
    for attempt in range(max_retries):
        try:
            return h5py.File(path, 'r')
        except (BlockingIOError, OSError) as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    raise last_err


# ── 데이터셋 ──────────────────────────────────────────────────────────────────
class BulbBCDataset(Dataset):
    """HDF5 파일들에서 (state, action) 쌍 로드.

    state  : [joint_pos(16), kinesthetic(12), tac_binary(4)]  float32
    action : [hand_target(16)]                                 float32

    demo_ranges : dict[str, tuple[int,int]] | None
        key   = 파일 경로에 포함된 문자열 (디렉토리명 등)
        value = (포함할 demo 번호 시작, 끝) — 양쪽 포함(inclusive)
        예)  {"2026_02_28_01_17_good_data_demo3to9": (3, 9),
              "2026_02_28_01_26_01_good_data_demo0to2": (0, 2)}
        매칭되지 않는 파일은 데모 범위 제한 없이 전부 로드.
    """

    def __init__(
        self,
        hdf5_paths: list[str],
        tactile_thresh: int = TACTILE_THRESH,
        demo_ranges: dict | None = None,
    ):
        states_list, actions_list = [], []
        total_demos = 0
        skipped = 0

        for path in hdf5_paths:
            # 이 파일에 적용할 demo 범위 결정
            lo, hi = 0, 10_000   # 기본: 모두 포함
            if demo_ranges:
                for key, (lo_k, hi_k) in demo_ranges.items():
                    if key in path:
                        lo, hi = lo_k, hi_k
                        break

            with _open_h5_read(path) as f:
                root = f.get('data', f)   # robomimic 형식: /data/demo_N
                for demo_key in sorted(root.keys()):
                    # demo_0, demo_1, … 형식 파싱
                    if not demo_key.startswith('demo_'):
                        continue
                    try:
                        demo_idx = int(demo_key.split('_', 1)[1])
                    except ValueError:
                        continue

                    if not (lo <= demo_idx <= hi):
                        skipped += 1
                        continue

                    demo = root[demo_key]
                    required = {
                        'Real_hand_joint_pos', 'Real_hand_kinesthetic',
                        'Real_hand_tactile',   'Real_hand_target',
                    }
                    if not required.issubset(demo.keys()):
                        print(f"  [SKIP] {path}/{demo_key}: 필수 키 없음")
                        continue

                    joint_pos   = demo['Real_hand_joint_pos'][:].astype(np.float32)    # (N,16)
                    kinesthetic = demo['Real_hand_kinesthetic'][:].astype(np.float32)  # (N,12)
                    tactile_raw = demo['Real_hand_tactile'][:]                         # (N,60)
                    target      = demo['Real_hand_target'][:].astype(np.float32)       # (N,16)
                    N = joint_pos.shape[0]

                    # 손가락별 접촉 binary (N,4) — 각 손가락 15센서 max > thresh
                    tac = tactile_raw.reshape(N, FINGERS, TACTILE_PER_FINGER)          # (N,4,15)
                    tac_binary = (tac.max(axis=2) > tactile_thresh).astype(np.float32) # (N,4)

                    state = np.concatenate([joint_pos, kinesthetic, tac_binary], axis=1)  # (N,32)
                    states_list.append(state)
                    actions_list.append(target)
                    total_demos += 1
                    print(f"  [LOAD] {os.path.basename(path)} / {demo_key}  ({N} samples)")

        if not states_list:
            raise RuntimeError(
                "로드된 데이터가 없습니다. "
                "파일 경로·demo_filter 범위·HDF5 키 구조(data/demo_N/Real_*)를 확인하세요.\n"
                "  - --data_dir 에 good_data 파일이 있는 디렉터리 지정 (예: ./logs/hdf5_recordings)\n"
                "  - demo_filter 의 '경로키'는 파일 전체 경로에 포함된 문자열이어야 함 (예: 파일명 일부)"
            )

        self.states  = np.concatenate(states_list,  axis=0)  # (Total, 32)
        self.actions = np.concatenate(actions_list, axis=0)  # (Total, 16)
        print(
            f"[DATA] 로드 {total_demos} demos | 스킵 {skipped} demos | "
            f"총 {len(self.states):,} samples"
        )

    def __len__(self) -> int:
        return len(self.states)

    def __getitem__(self, idx):
        return (
            torch.from_numpy(self.states[idx]),
            torch.from_numpy(self.actions[idx]),
        )


# ── 정규화 ────────────────────────────────────────────────────────────────────
class Normalizer:
    """z-score 정규화 (mean=0, std=1)."""

    def __init__(self, data: np.ndarray, eps: float = 1e-6):
        self.mean = data.mean(0).astype(np.float32)
        self.std  = data.std(0).clip(eps).astype(np.float32)

    def normalize(self, x: np.ndarray) -> np.ndarray:
        return (x - self.mean) / self.std

    def denormalize(self, x: np.ndarray) -> np.ndarray:
        return x * self.std + self.mean

    def save(self, path: str):
        np.savez(path, mean=self.mean, std=self.std)
        print(f"  저장: {path}")

    @classmethod
    def load(cls, path: str) -> 'Normalizer':
        obj = cls.__new__(cls)
        d = np.load(path)
        obj.mean = d['mean'].astype(np.float32)
        obj.std  = d['std'].astype(np.float32)
        return obj

    def to_torch(self, device):
        return (
            torch.from_numpy(self.mean).to(device),
            torch.from_numpy(self.std).to(device),
        )


# ── 모델 ──────────────────────────────────────────────────────────────────────
class BCMLP(nn.Module):
    """3-hidden-layer MLP with LayerNorm + ReLU + Dropout."""

    def __init__(
        self,
        state_dim:  int = STATE_DIM,
        action_dim: int = ACTION_DIM,
        hidden:     int = 256,
        dropout:    float = 0.1,
    ):
        super().__init__()

        def block(in_d: int, out_d: int) -> nn.Sequential:
            return nn.Sequential(
                nn.Linear(in_d, out_d),
                nn.LayerNorm(out_d),
                nn.ReLU(),
                nn.Dropout(dropout),
            )

        self.net = nn.Sequential(
            block(state_dim, hidden),
            block(hidden,    hidden),
            block(hidden,    hidden),
            nn.Linear(hidden, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ── 학습 ──────────────────────────────────────────────────────────────────────
class _NormDataset(Dataset):
    """state/action z-score 적용 래퍼."""

    def __init__(self, base: Dataset, s_norm: Normalizer, a_norm: Normalizer):
        self.base   = base
        self.s_norm = s_norm
        self.a_norm = a_norm

    def __len__(self) -> int:
        return len(self.base)

    def __getitem__(self, idx):
        s, a = self.base[idx]
        return (
            torch.from_numpy(self.s_norm.normalize(s.numpy())),
            torch.from_numpy(self.a_norm.normalize(a.numpy())),
        )


def _expand_to_hdf5(path: str) -> list[str]:
    """경로가 디렉토리면 내부 .hdf5 파일 목록 반환, 파일이면 그대로 반환."""
    if os.path.isdir(path):
        return sorted(glob.glob(os.path.join(path, '**', '*.hdf5'), recursive=True))
    return [path]


def _resolve_files(args) -> list[str]:
    """사용할 HDF5 파일 목록 결정.

    우선순위:
      1. --files  : 직접 지정 (공백/쉼표 구분, glob 패턴/디렉토리 지원)
      2. --list   : 파일 경로가 한 줄씩 적힌 텍스트 파일
      3. --data_dir + --exclude : 디렉토리 전체에서 제외 파일 필터링
    """
    # ── 방법 1: 직접 지정 ──
    if args.files:
        files = []
        for token in args.files:
            for part in token.split(','):
                part = part.strip()
                if not part:
                    continue
                matched = sorted(glob.glob(part, recursive=True))
                targets = matched if matched else [part]
                for t in targets:
                    files.extend(_expand_to_hdf5(t))
        return files

    # ── 방법 2: 리스트 파일 ──
    if args.list:
        with open(args.list) as f:
            lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith('#')]
        files = []
        for ln in lines:
            files.extend(_expand_to_hdf5(ln))
        return files

    # ── 방법 3: 디렉토리 전체 (제외 목록 적용) ──
    all_files = sorted(
        glob.glob(os.path.join(args.data_dir, '**', '*.hdf5'), recursive=True)
    )
    if args.exclude:
        exclude_set = set()
        for token in args.exclude:
            for part in token.split(','):
                part = part.strip()
                matched = glob.glob(part, recursive=True)
                exclude_set.update(matched if matched else [part])
        all_files = [f for f in all_files if f not in exclude_set]
    return all_files


def _parse_demo_filter(filter_args: list[str] | None) -> dict | None:
    """'폴더명:start-end' 문자열 목록 → demo_ranges dict.

    예) ["2026_02_28_01_17_good_data_demo3to9:3-9",
          "2026_02_28_01_26_01_good_data_demo0to2:0-2"]
        →  {"2026_02_28_01_17_good_data_demo3to9": (3, 9),
             "2026_02_28_01_26_01_good_data_demo0to2": (0, 2)}
    """
    if not filter_args:
        return None
    ranges = {}
    for token in filter_args:
        token = token.strip()
        if ':' not in token:
            raise ValueError(f"--demo_filter 형식 오류: '{token}'  →  'path_key:start-end' 로 작성하세요.")
        path_key, rng = token.rsplit(':', 1)
        if '-' not in rng:
            raise ValueError(f"--demo_filter 범위 형식 오류: '{rng}'  →  '3-9' 처럼 작성하세요.")
        start, end = rng.split('-', 1)
        ranges[path_key.strip()] = (int(start), int(end))
    return ranges


def train():
    # 스크립트 위치 기준 기본 데이터 디렉터리 (실행 경로와 무관하게 동작)
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _default_data_dir = os.path.join(_script_dir, 'logs', 'hdf5_recordings')

    parser = argparse.ArgumentParser(
        description='BC 학습 — KISTAR Hand 전구 돌리기',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # ── 파일 선택 (3가지 방법 중 하나 사용) ──
    parser.add_argument(
        '--data_dir', default=_default_data_dir,
        help='[방법3] HDF5 디렉토리 (기본값: 스크립트경로/logs/hdf5_recordings)',
    )
    parser.add_argument(
        '--files', nargs='+', default=None,
        help=(
            '[방법1] 사용할 파일을 직접 지정 (glob 패턴/공백/쉼표 구분)\n'
            '  예) --files ./HDF5/2026_02_28_10_00.hdf5 ./HDF5/2026_02_28_11_00.hdf5\n'
            '  예) --files "./HDF5/2026_02_28_*.hdf5"'
        ),
    )
    parser.add_argument(
        '--list', default=None,
        help=(
            '[방법2] 파일 경로가 한 줄씩 적힌 텍스트 파일 경로\n'
            '  예) --list ./train_files.txt'
        ),
    )
    parser.add_argument(
        '--exclude', nargs='+', default=None,
        help=(
            '[방법3 보조] 제외할 파일 (glob 패턴/공백/쉼표 구분)\n'
            '  예) --exclude ./HDF5/2026_02_28_09_00.hdf5'
        ),
    )
    parser.add_argument(
        '--demo_filter', nargs='+', default=None,
        help=(
            '특정 파일/폴더에서 demo 번호 범위 지정  형식: "경로키:start-end"\n'
            '  경로키 = 파일 경로에 포함된 문자열 (폴더명 등)\n'
            '  예) --demo_filter \\\n'
            '        "2026_02_28_01_17_good_data_demo3to9:3-9" \\\n'
            '        "2026_02_28_01_26_01_good_data_demo0to2:0-2"'
        ),
    )
    # ── 학습 하이퍼파라미터 ──
    parser.add_argument('--out_dir',    default='./bc_model',  help='모델/정규화 저장 경로')
    parser.add_argument('--epochs',     type=int,   default=300)
    parser.add_argument('--batch',      type=int,   default=512)
    parser.add_argument('--lr',         type=float, default=1e-3)
    parser.add_argument('--hidden',     type=int,   default=256)
    parser.add_argument('--dropout',    type=float, default=0.1)
    parser.add_argument('--val_ratio',  type=float, default=0.1,  help='검증 데이터 비율')
    parser.add_argument('--patience',   type=int,   default=40,   help='Early stopping patience')
    parser.add_argument('--seed',       type=int,   default=42)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    # ── 파일 결정 ──
    hdf5_files = _resolve_files(args)
    if not hdf5_files:
        print("[ERROR] 사용할 HDF5 파일이 없습니다.")
        print("  --files, --list, 또는 --data_dir 옵션을 확인하세요.")
        return
    print(f"[DATA] {len(hdf5_files)}개 파일 사용:")
    for f in hdf5_files:
        exists = "OK" if os.path.exists(f) else "없음"
        print(f"  [{exists}] {f}")

    # ── demo 범위 파싱 ──
    demo_ranges = _parse_demo_filter(args.demo_filter)
    if demo_ranges:
        print("[FILTER] demo 범위 적용:")
        for k, (lo, hi) in demo_ranges.items():
            print(f"  '{k}' → demo_{lo} ~ demo_{hi}")

    # ── 데이터 로드 ──
    dataset = BulbBCDataset(hdf5_files, demo_ranges=demo_ranges)
    n_total = len(dataset)
    n_val   = max(1, int(n_total * args.val_ratio))
    n_train = n_total - n_val
    train_ds, val_ds = random_split(
        dataset, [n_train, n_val],
        generator=torch.Generator().manual_seed(args.seed),
    )

    # ── 정규화 파라미터 계산 (전체 데이터 기준) ──
    print("[NORM] 정규화 파라미터 계산 중...")
    state_norm  = Normalizer(dataset.states)
    action_norm = Normalizer(dataset.actions)
    state_norm.save(os.path.join(args.out_dir,  'state_norm.npz'))
    action_norm.save(os.path.join(args.out_dir, 'action_norm.npz'))

    # ── DataLoader ──
    train_loader = DataLoader(
        _NormDataset(train_ds, state_norm, action_norm),
        batch_size=args.batch, shuffle=True,  num_workers=2, pin_memory=True,
    )
    val_loader = DataLoader(
        _NormDataset(val_ds, state_norm, action_norm),
        batch_size=args.batch, shuffle=False, num_workers=2, pin_memory=True,
    )

    # ── 모델 / 옵티마이저 ──
    device    = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model     = BCMLP(STATE_DIM, ACTION_DIM, args.hidden, args.dropout).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs, eta_min=1e-5,
    )
    criterion = nn.MSELoss()

    total_params = sum(p.numel() for p in model.parameters())
    print(
        f"[MODEL] {total_params:,} params | device={device} | "
        f"train={n_train:,} | val={n_val:,}"
    )
    print(
        f"[TRAIN] epochs={args.epochs} | batch={args.batch} | "
        f"lr={args.lr} | hidden={args.hidden} | dropout={args.dropout}"
    )
    print("-" * 60)

    # ── 학습 루프 ──
    best_val_loss = float('inf')
    patience_cnt  = 0

    for epoch in range(1, args.epochs + 1):
        # Train
        model.train()
        train_loss = 0.0
        for s, a in train_loader:
            s, a = s.to(device), a.to(device)
            loss = criterion(model(s), a)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            train_loss += loss.item() * s.size(0)
        train_loss /= n_train

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for s, a in val_loader:
                s, a = s.to(device), a.to(device)
                val_loss += criterion(model(s), a).item() * s.size(0)
        val_loss /= n_val

        scheduler.step()

        if epoch % 10 == 0 or epoch == 1:
            lr_now = scheduler.get_last_lr()[0]
            mark = " *" if val_loss < best_val_loss else ""
            print(
                f"[{epoch:4d}/{args.epochs}] "
                f"train={train_loss:.5f}  val={val_loss:.5f}  "
                f"lr={lr_now:.6f}{mark}"
            )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_cnt  = 0
            torch.save(
                {
                    'epoch':      epoch,
                    'state_dim':  STATE_DIM,
                    'action_dim': ACTION_DIM,
                    'hidden':     args.hidden,
                    'dropout':    args.dropout,
                    'val_loss':   val_loss,
                    'model_state': model.state_dict(),
                },
                os.path.join(args.out_dir, 'bc_best.pt'),
            )
        else:
            patience_cnt += 1
            if patience_cnt >= args.patience:
                print(f"[EARLY STOP] epoch {epoch} | patience {args.patience} 도달")
                break

    print("=" * 60)
    print(f"[DONE] 최종 best val loss : {best_val_loss:.5f}")
    print(f"[DONE] 모델    : {args.out_dir}/bc_best.pt")
    print(f"[DONE] 정규화  : {args.out_dir}/state_norm.npz, action_norm.npz")


if __name__ == '__main__':
    train()
