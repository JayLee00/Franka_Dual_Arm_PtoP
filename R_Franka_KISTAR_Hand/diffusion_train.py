#!/usr/bin/env python3
"""
Low-D Diffusion Policy 학습 스크립트 — KISTAR Hand 전구 돌리기 태스크

아키텍처:
  1. MLP Observation Encoder : obs_seq(T_obs, 32) → global_cond(256)
  2. 1D U-Net Denoiser       : noisy_action(T_pred, 16) + timestep + cond → pred_noise

노이즈 스케줄 : Cosine DDPM (T=100)
추론           : DDIM (결정적, 10스텝)
액션 청킹      : T_obs=2, T_pred=16, T_exec=8

HDF5 키 (data/demo_N/):
  Real_hand_joint_pos   (N, 16) int16   ← 현재 관절각
  Real_hand_kinesthetic (N, 12) int16   ← 역감 센서
  Real_hand_tactile     (N, 60) int16   ← 촉각 센서
  Real_hand_target      (N, 16) int16   ← 목표 관절각 (action)

학습 예시:
  python3 diffusion_train.py \\
      --data_dir ./logs/hdf5_recordings \\
      --demo_filter \\
          "2026_02_28_01_17_good_data_demo3to9:3-9" \\
          "2026_02_28_01_26_01_good_data_demo0to2:0-2" \\
      --epochs 600 --batch 256

출력:
  dp_model/dp_best.pt       ← obs_encoder + noise_pred_net
  dp_model/obs_norm.npz     ← 관찰 정규화 파라미터
  dp_model/act_norm.npz     ← 액션 정규화 파라미터
"""

import argparse
import glob
import math
import os
import time

import h5py
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, random_split

# ══════════════════════════════════════════════════════════════════════
# 상수
# ══════════════════════════════════════════════════════════════════════
TACTILE_THRESH    = 1000
FINGERS           = 4
TACTILE_PER_FINGER= 15
OBS_DIM           = 16 + 12 + 4   # joint_pos + kinesthetic + tac_binary = 32
ACTION_DIM        = 16

OBS_HORIZON   = 2     # 관찰 윈도우 길이 (현재 + 과거 1)
PRED_HORIZON  = 16    # 예측 액션 시퀀스 길이
ACTION_STEPS  = 8     # 매 추론마다 실행할 스텝 수
DIFF_STEPS    = 100   # DDPM 확산 스텝
INFER_STEPS   = 10    # DDIM 추론 스텝


# ══════════════════════════════════════════════════════════════════════
# DDPM 노이즈 스케줄러 (Cosine)
# ══════════════════════════════════════════════════════════════════════
class DDPMScheduler:
    """Cosine 노이즈 스케줄러 (Ho+ 2020, Nichol+ 2021)."""

    def __init__(self, num_steps: int = DIFF_STEPS):
        T = num_steps
        s = 0.008
        t = torch.arange(T + 1, dtype=torch.float64)
        f = torch.cos(((t / T + s) / (1.0 + s)) * math.pi / 2.0) ** 2
        alpha_bar = (f / f[0]).float()
        betas     = (1 - alpha_bar[1:] / alpha_bar[:-1]).clamp(max=0.999)
        alphas    = 1.0 - betas
        alpha_bar = torch.cumprod(alphas, dim=0)
        alpha_bar_prev = F.pad(alpha_bar[:-1], (1, 0), value=1.0)

        self.T              = T
        self.alpha_bar      = alpha_bar
        self.alpha_bar_prev = alpha_bar_prev
        self.sqrt_ab        = alpha_bar.sqrt()
        self.sqrt_1m_ab     = (1 - alpha_bar).sqrt()

    # ── 학습용 ────────────────────────────────────────────────────────
    def add_noise(self, x0: torch.Tensor, noise: torch.Tensor,
                  t: torch.Tensor) -> torch.Tensor:
        """q(x_t|x_0) = sqrt(ab_t)*x0 + sqrt(1-ab_t)*noise"""
        ab   = self.sqrt_ab[t].to(x0.device)[:, None, None]
        s1ab = self.sqrt_1m_ab[t].to(x0.device)[:, None, None]
        return ab * x0 + s1ab * noise

    # ── 추론용: DDIM (eta=0, 결정적) ─────────────────────────────────
    @torch.no_grad()
    def ddim_step(self, pred_noise: torch.Tensor, t_curr: int, t_prev: int,
                  x_t: torch.Tensor) -> torch.Tensor:
        """DDIM 역방향 한 스텝.
        t_prev = -1 이면 최종 스텝으로 처리 (alpha_bar_prev = 1.0).
        """
        dev    = x_t.device
        ab     = self.alpha_bar[t_curr].to(dev)
        ab_prev = (self.alpha_bar[t_prev].to(dev)
                   if t_prev >= 0 else torch.tensor(1.0, device=dev))

        x0_pred = (x_t - (1 - ab).sqrt() * pred_noise) / ab.sqrt()
        x0_pred = x0_pred.clamp(-3.0, 3.0)
        # DDIM (eta=0): deterministic
        return ab_prev.sqrt() * x0_pred + (1 - ab_prev).sqrt() * pred_noise

    def get_infer_timesteps(self, n_steps: int = INFER_STEPS) -> list:
        """추론용 등간격 타임스텝 리스트 (내림차순)."""
        step = max(1, self.T // n_steps)
        return list(range(self.T - 1, -1, -step))[:n_steps]


# ══════════════════════════════════════════════════════════════════════
# 네트워크 구성 요소
# ══════════════════════════════════════════════════════════════════════
class SinusoidalPosEmb(nn.Module):
    """정현파 타임스텝 임베딩."""

    def __init__(self, dim: int):
        super().__init__()
        self.dim = dim

    def forward(self, t: torch.Tensor) -> torch.Tensor:  # t: (B,) long
        half = self.dim // 2
        freq = torch.exp(
            -math.log(10000)
            * torch.arange(half, device=t.device, dtype=torch.float32)
            / (half - 1)
        )
        emb = t.float()[:, None] * freq[None, :]          # (B, half)
        return torch.cat([emb.sin(), emb.cos()], dim=-1)  # (B, dim)


class ConvResBlock(nn.Module):
    """1D 잔차 블록 + FiLM 조건화 (scale/shift)."""

    def __init__(self, in_ch: int, out_ch: int, cond_dim: int, kernel_size: int = 3):
        super().__init__()
        pad = kernel_size // 2
        # GroupNorm groups: 8 if divisible, else 4, else 1
        ng  = 8 if out_ch % 8 == 0 else (4 if out_ch % 4 == 0 else 1)
        self.conv1    = nn.Conv1d(in_ch,  out_ch, kernel_size, padding=pad)
        self.conv2    = nn.Conv1d(out_ch, out_ch, kernel_size, padding=pad)
        self.norm1    = nn.GroupNorm(ng, out_ch)
        self.norm2    = nn.GroupNorm(ng, out_ch)
        self.act      = nn.Mish()
        self.film     = nn.Linear(cond_dim, 2 * out_ch)   # → scale, shift
        self.shortcut = nn.Conv1d(in_ch, out_ch, 1) if in_ch != out_ch else nn.Identity()

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        # x: (B, in_ch, T),  cond: (B, cond_dim)
        scale, shift = self.film(cond).chunk(2, dim=-1)   # each: (B, out_ch)
        h = self.act(self.norm1(self.conv1(x)))
        h = h * (1 + scale[:, :, None]) + shift[:, :, None]   # FiLM
        h = self.act(self.norm2(self.conv2(h)))
        return h + self.shortcut(x)


class MLPObsEncoder(nn.Module):
    """MLP 관찰 인코더 : obs_seq (B, T_obs, OBS_DIM) → global_cond (B, out_dim)."""

    def __init__(self, obs_dim: int = OBS_DIM, obs_horizon: int = OBS_HORIZON,
                 out_dim: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim * obs_horizon, 256),
            nn.LayerNorm(256),
            nn.Mish(),
            nn.Linear(256, out_dim),
            nn.LayerNorm(out_dim),
            nn.Mish(),
        )

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        return self.net(obs.flatten(1))   # (B, out_dim)


class ConditionalUnet1D(nn.Module):
    """1D U-Net 디노이저 (FiLM 조건화).

    channels = (C0, C1, C2) 기준:
      Stem     : action_dim → C0
      Enc 0    : ResBlock(C0→C0), DS
      Enc 1    : ResBlock(C0→C1), DS
      Mid      : ResBlock(C1→C2), ResBlock(C2→C2)
      Dec 0    : US(C2), cat(skip1=C1) → ResBlock(C2+C1→C1)
      Dec 1    : US(C1), cat(skip0=C0) → ResBlock(C1+C0→C0)
      Head     : Conv1d(C0 → action_dim)

    T_pred=16 기준: 16 → DS→8 → DS→4 → US→8 → US→16
    """

    def __init__(
        self,
        action_dim:      int   = ACTION_DIM,
        global_cond_dim: int   = 256,
        time_emb_dim:    int   = 128,
        channels:        tuple = (64, 128, 256),
        kernel_size:     int   = 3,
    ):
        super().__init__()

        # 타임스텝 임베딩
        self.time_mlp = nn.Sequential(
            SinusoidalPosEmb(time_emb_dim),
            nn.Linear(time_emb_dim, time_emb_dim * 4),
            nn.Mish(),
            nn.Linear(time_emb_dim * 4, time_emb_dim),
        )
        cond_dim = time_emb_dim + global_cond_dim   # 128 + 256 = 384

        # ── Stem ──────────────────────────────────────────────────────
        self.stem = nn.Conv1d(action_dim, channels[0], kernel_size,
                              padding=kernel_size // 2)

        # ── Encoder ───────────────────────────────────────────────────
        # enc_in/out channels per level
        n_down   = len(channels) - 1
        enc_in   = [channels[0]] + list(channels[:-2])   # [C0, C0]  for 3-ch
        enc_out  = list(channels[:-1])                   # [C0, C1]

        self.enc_blocks = nn.ModuleList([
            ConvResBlock(enc_in[i], enc_out[i], cond_dim, kernel_size)
            for i in range(n_down)
        ])
        self.enc_ds = nn.ModuleList([
            nn.Conv1d(enc_out[i], enc_out[i], 4, stride=2, padding=1)
            for i in range(n_down)
        ])

        # ── Bottleneck ────────────────────────────────────────────────
        self.mid_blocks = nn.ModuleList([
            ConvResBlock(channels[-2], channels[-1], cond_dim, kernel_size),
            ConvResBlock(channels[-1], channels[-1], cond_dim, kernel_size),
        ])

        # ── Decoder ───────────────────────────────────────────────────
        # dec[0]: US(C2→C2), cat(skip=C1) → ResBlock(C2+C1→C1)
        # dec[1]: US(C1→C1), cat(skip=C0) → ResBlock(C1+C0→C0)
        dec_us_in  = list(reversed(channels[1:]))    # [C2, C1]
        dec_skip   = list(reversed(channels[:-1]))   # [C1, C0]
        dec_out    = list(reversed(channels[:-1]))   # [C1, C0]

        self.dec_us = nn.ModuleList([
            nn.ConvTranspose1d(dec_us_in[i], dec_us_in[i], 4, stride=2, padding=1)
            for i in range(n_down)
        ])
        self.dec_blocks = nn.ModuleList([
            ConvResBlock(dec_us_in[i] + dec_skip[i], dec_out[i], cond_dim, kernel_size)
            for i in range(n_down)
        ])

        # ── Head ──────────────────────────────────────────────────────
        self.head = nn.Conv1d(channels[0], action_dim, kernel_size,
                              padding=kernel_size // 2)

    def forward(self, noisy_actions: torch.Tensor, timestep: torch.Tensor,
                global_cond: torch.Tensor) -> torch.Tensor:
        """
        Args:
            noisy_actions : (B, T_pred, action_dim)
            timestep      : (B,) long
            global_cond   : (B, global_cond_dim)
        Returns:
            pred_noise    : (B, T_pred, action_dim)
        """
        x    = noisy_actions.permute(0, 2, 1)               # (B, action_dim, T)
        t_emb = self.time_mlp(timestep)                      # (B, time_emb_dim)
        cond  = torch.cat([t_emb, global_cond], dim=-1)      # (B, cond_dim)

        x = self.stem(x)                                     # (B, C0, T)

        # Encoder
        skips = []
        for block, ds in zip(self.enc_blocks, self.enc_ds):
            x = block(x, cond)
            skips.append(x)
            x = ds(x)

        # Bottleneck
        for block in self.mid_blocks:
            x = block(x, cond)

        # Decoder
        for us, block in zip(self.dec_us, self.dec_blocks):
            x    = us(x)
            skip = skips.pop()
            if x.shape[-1] != skip.shape[-1]:
                x = F.interpolate(x, size=skip.shape[-1], mode='nearest')
            x = torch.cat([x, skip], dim=1)
            x = block(x, cond)

        return self.head(x).permute(0, 2, 1)   # (B, T, action_dim)


# ══════════════════════════════════════════════════════════════════════
# 데이터셋 — 슬라이딩 윈도우
# ══════════════════════════════════════════════════════════════════════
class BulbDiffDataset(Dataset):
    """HDF5 파일에서 (obs_seq, act_seq) 윈도우 로드.

    obs_seq : (T_obs,  OBS_DIM)    float32  — 정규화 전
    act_seq : (T_pred, ACTION_DIM) float32  — 정규화 전

    슬라이딩 윈도우 인덱스 t:
      obs_seq = state[t-T_obs+1 : t+1]
      act_seq = target[t : t+T_pred]
    """

    def __init__(
        self,
        hdf5_paths:     list,
        obs_horizon:    int  = OBS_HORIZON,
        pred_horizon:   int  = PRED_HORIZON,
        tactile_thresh: int  = TACTILE_THRESH,
        demo_ranges:    dict = None,
    ):
        self.T_obs  = obs_horizon
        self.T_pred = pred_horizon

        obs_list, act_list = [], []
        total_demos = 0

        for path in hdf5_paths:
            lo, hi = 0, 10_000
            if demo_ranges:
                for key, (lo_k, hi_k) in demo_ranges.items():
                    if key in path:
                        lo, hi = lo_k, hi_k
                        break

            try:
                hf = h5py.File(path, 'r')
            except OSError as e:
                print(f"  [SKIP] {os.path.basename(path)}: HDF5 열기 실패 ({e})")
                continue

            with hf as f:
                root = f.get('data', f)
                for demo_key in sorted(root.keys()):
                    if not demo_key.startswith('demo_'):
                        continue
                    try:
                        demo_idx = int(demo_key.split('_', 1)[1])
                    except ValueError:
                        continue
                    if not (lo <= demo_idx <= hi):
                        continue

                    demo = root[demo_key]
                    required = {
                        'Real_hand_joint_pos', 'Real_hand_kinesthetic',
                        'Real_hand_tactile',   'Real_hand_target',
                    }
                    if not required.issubset(demo.keys()):
                        print(f"  [SKIP] {path}/{demo_key}: 필수 키 없음")
                        continue

                    jp  = demo['Real_hand_joint_pos'][:].astype(np.float32)     # (N,16)
                    kin = demo['Real_hand_kinesthetic'][:].astype(np.float32)   # (N,12)
                    tac = demo['Real_hand_tactile'][:]                          # (N,60)
                    tgt = demo['Real_hand_target'][:].astype(np.float32)        # (N,16)
                    N   = jp.shape[0]

                    # tactile binary per finger (N,4)
                    tac_bin = (
                        tac.reshape(N, FINGERS, TACTILE_PER_FINGER)
                           .max(axis=2) > tactile_thresh
                    ).astype(np.float32)

                    state = np.concatenate([jp, kin, tac_bin], axis=1)   # (N, 32)

                    n_win = N - obs_horizon - pred_horizon + 2
                    if n_win <= 0:
                        print(f"  [SKIP] {demo_key}: N={N} 짧음")
                        continue

                    for t in range(obs_horizon - 1, N - pred_horizon + 1):
                        obs_list.append(state[t - obs_horizon + 1: t + 1])  # (T_obs, 32)
                        act_list.append(tgt[t: t + pred_horizon])           # (T_pred, 16)

                    total_demos += 1
                    print(f"  [LOAD] {os.path.basename(path)} / {demo_key}"
                          f"  N={N}  →  {n_win} windows")

        if not obs_list:
            raise RuntimeError(
                "데이터 없음: 경로/demo_filter/HDF5 구조 확인\n"
                "  키 확인: data/demo_N/Real_hand_{joint_pos,kinesthetic,tactile,target}"
            )

        self.obs_seq = np.stack(obs_list, axis=0)   # (M, T_obs, 32)
        self.act_seq = np.stack(act_list, axis=0)   # (M, T_pred, 16)
        print(f"[DATA] {total_demos} demos  |  {len(self.obs_seq):,} windows")

    def __len__(self):
        return len(self.obs_seq)

    def __getitem__(self, idx):
        return (
            torch.from_numpy(self.obs_seq[idx].copy()),
            torch.from_numpy(self.act_seq[idx].copy()),
        )


# ══════════════════════════════════════════════════════════════════════
# 정규화
# ══════════════════════════════════════════════════════════════════════
class Normalizer:
    """z-score 정규화 (per-feature, 시퀀스 전체 flatten 후 통계 계산)."""

    def __init__(self, data: np.ndarray, eps: float = 1e-6):
        flat = data.reshape(-1, data.shape[-1])
        self.mean = flat.mean(0).astype(np.float32)
        self.std  = flat.std(0).clip(eps).astype(np.float32)

    def normalize(self, x: np.ndarray) -> np.ndarray:
        return (x - self.mean) / self.std

    def denormalize(self, x: np.ndarray) -> np.ndarray:
        return x * self.std + self.mean

    def save(self, path: str):
        np.savez(path, mean=self.mean, std=self.std)
        print(f"  저장: {path}")

    @classmethod
    def load(cls, path: str):
        obj = object.__new__(cls)
        d = np.load(path)
        obj.mean = d['mean'].astype(np.float32)
        obj.std  = d['std'].astype(np.float32)
        return obj

    def to_torch(self, device='cpu'):
        return (
            torch.from_numpy(self.mean).to(device),
            torch.from_numpy(self.std).to(device),
        )


class _NormDataset(Dataset):
    """obs/action z-score 적용 래퍼."""

    def __init__(self, base: Dataset, obs_norm: Normalizer, act_norm: Normalizer):
        self.base     = base
        self.obs_norm = obs_norm
        self.act_norm = act_norm

    def __len__(self):
        return len(self.base)

    def __getitem__(self, idx):
        obs, act = self.base[idx]
        return (
            torch.from_numpy(self.obs_norm.normalize(obs.numpy())),
            torch.from_numpy(self.act_norm.normalize(act.numpy())),
        )


# ══════════════════════════════════════════════════════════════════════
# 파일 선택 유틸 (bc_train.py 와 동일)
# ══════════════════════════════════════════════════════════════════════
def _expand_to_hdf5(path: str) -> list:
    if os.path.isdir(path):
        return sorted(glob.glob(os.path.join(path, '**', '*.hdf5'), recursive=True))
    return [path]


def _resolve_files(args) -> list:
    if args.files:
        files = []
        for token in args.files:
            for part in token.split(','):
                part = part.strip()
                if not part:
                    continue
                matched = sorted(glob.glob(part, recursive=True))
                for t in (matched if matched else [part]):
                    files.extend(_expand_to_hdf5(t))
        return files

    if args.list:
        with open(args.list) as f:
            lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith('#')]
        files = []
        for ln in lines:
            files.extend(_expand_to_hdf5(ln))
        return files

    all_files = sorted(
        glob.glob(os.path.join(args.data_dir, '**', '*.hdf5'), recursive=True)
    )
    if args.exclude:
        excl = set()
        for token in args.exclude:
            for part in token.split(','):
                part = part.strip()
                excl.update(glob.glob(part, recursive=True) or [part])
        all_files = [f for f in all_files if f not in excl]
    return all_files


def _parse_demo_filter(filter_args) -> dict:
    if not filter_args:
        return None
    ranges = {}
    for token in filter_args:
        token = token.strip()
        if ':' not in token:
            raise ValueError(f"demo_filter 형식 오류: '{token}'  →  'path_key:start-end'")
        path_key, rng = token.rsplit(':', 1)
        start, end = rng.split('-', 1)
        ranges[path_key.strip()] = (int(start), int(end))
    return ranges


# ══════════════════════════════════════════════════════════════════════
# 학습
# ══════════════════════════════════════════════════════════════════════
def train():
    _script_dir      = os.path.dirname(os.path.abspath(__file__))
    _default_data    = os.path.join(_script_dir, 'logs', 'hdf5_recordings')

    parser = argparse.ArgumentParser(
        description='Low-D Diffusion Policy 학습 — KISTAR Hand 전구 돌리기',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # 파일 선택
    parser.add_argument('--data_dir', default=_default_data)
    parser.add_argument('--files',   nargs='+', default=None)
    parser.add_argument('--list',    default=None)
    parser.add_argument('--exclude', nargs='+', default=None)
    parser.add_argument(
        '--demo_filter', nargs='+', default=None,
        help=(
            'demo 범위 지정  형식: "경로키:start-end"\n'
            '  예) --demo_filter \\\n'
            '        "2026_02_28_01_17_good_data_demo3to9:3-9" \\\n'
            '        "2026_02_28_01_26_01_good_data_demo0to2:0-2"'
        ),
    )
    # 하이퍼파라미터
    parser.add_argument('--out_dir',    default='./dp_model')
    parser.add_argument('--epochs',     type=int,   default=600)
    parser.add_argument('--batch',      type=int,   default=256)
    parser.add_argument('--lr',         type=float, default=1e-4)
    parser.add_argument('--val_ratio',  type=float, default=0.1)
    parser.add_argument('--patience',   type=int,   default=60)
    parser.add_argument('--seed',       type=int,   default=42)
    # 아키텍처
    parser.add_argument('--obs_horizon',  type=int, default=OBS_HORIZON)
    parser.add_argument('--pred_horizon', type=int, default=PRED_HORIZON)
    parser.add_argument('--diff_steps',   type=int, default=DIFF_STEPS)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    # ── 파일 결정 ──
    hdf5_files = _resolve_files(args)
    if not hdf5_files:
        print("[ERROR] HDF5 파일 없음. --files / --data_dir 확인")
        return
    print(f"[DATA] 사용 파일 {len(hdf5_files)}개:")
    for f in hdf5_files:
        print(f"  {'OK' if os.path.exists(f) else '없음':3s} {f}")

    demo_ranges = _parse_demo_filter(args.demo_filter)
    if demo_ranges:
        print("[FILTER] demo 범위:")
        for k, (lo, hi) in demo_ranges.items():
            print(f"  '{k}' → demo_{lo}~{hi}")

    # ── 데이터셋 & 정규화 ──
    dataset = BulbDiffDataset(
        hdf5_files,
        obs_horizon=args.obs_horizon,
        pred_horizon=args.pred_horizon,
        demo_ranges=demo_ranges,
    )
    obs_norm = Normalizer(dataset.obs_seq)
    act_norm = Normalizer(dataset.act_seq)
    obs_norm.save(os.path.join(args.out_dir, 'obs_norm.npz'))
    act_norm.save(os.path.join(args.out_dir, 'act_norm.npz'))

    n_total = len(dataset)
    n_val   = max(1, int(n_total * args.val_ratio))
    n_train = n_total - n_val
    train_ds, val_ds = random_split(
        dataset, [n_train, n_val],
        generator=torch.Generator().manual_seed(args.seed),
    )
    train_loader = DataLoader(
        _NormDataset(train_ds, obs_norm, act_norm),
        batch_size=args.batch, shuffle=True, num_workers=2, pin_memory=True,
    )
    val_loader = DataLoader(
        _NormDataset(val_ds, obs_norm, act_norm),
        batch_size=args.batch, shuffle=False, num_workers=2, pin_memory=True,
    )

    # ── 모델 ──
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    obs_encoder = MLPObsEncoder(
        obs_dim=OBS_DIM, obs_horizon=args.obs_horizon, out_dim=256
    ).to(device)

    noise_pred_net = ConditionalUnet1D(
        action_dim=ACTION_DIM,
        global_cond_dim=256,
        time_emb_dim=128,
        channels=(64, 128, 256),
        kernel_size=3,
    ).to(device)

    scheduler = DDPMScheduler(args.diff_steps)

    params = list(obs_encoder.parameters()) + list(noise_pred_net.parameters())
    optimizer = torch.optim.Adam(params, lr=args.lr, weight_decay=1e-5)
    lr_sched  = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs, eta_min=1e-6,
    )

    n_obs_p   = sum(p.numel() for p in obs_encoder.parameters())
    n_unet_p  = sum(p.numel() for p in noise_pred_net.parameters())
    print(f"[MODEL] OBS encoder: {n_obs_p:,} | U-Net: {n_unet_p:,} | "
          f"total: {n_obs_p+n_unet_p:,}  device={device}")
    print(f"[TRAIN] epochs={args.epochs} batch={args.batch} lr={args.lr} "
          f"train={n_train:,} val={n_val:,}")
    print("-" * 65)

    # ── 학습 루프 ──
    best_val_loss = float('inf')
    patience_cnt  = 0

    for epoch in range(1, args.epochs + 1):
        # Train
        obs_encoder.train()
        noise_pred_net.train()
        train_loss = 0.0

        for obs_seq, act_seq in train_loader:
            obs_seq = obs_seq.to(device)   # (B, T_obs, 32)
            act_seq = act_seq.to(device)   # (B, T_pred, 16)
            B = obs_seq.size(0)

            t     = torch.randint(0, args.diff_steps, (B,), device=device)
            noise = torch.randn_like(act_seq)
            x_t   = scheduler.add_noise(act_seq, noise, t.cpu())
            x_t   = x_t.to(device)

            global_cond = obs_encoder(obs_seq)             # (B, 256)
            pred_noise  = noise_pred_net(x_t, t, global_cond)  # (B, T_pred, 16)

            loss = F.mse_loss(pred_noise, noise)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, max_norm=1.0)
            optimizer.step()
            train_loss += loss.item() * B

        train_loss /= n_train

        # Validation
        obs_encoder.eval()
        noise_pred_net.eval()
        val_loss = 0.0
        with torch.no_grad():
            for obs_seq, act_seq in val_loader:
                obs_seq = obs_seq.to(device)
                act_seq = act_seq.to(device)
                B = obs_seq.size(0)
                t     = torch.randint(0, args.diff_steps, (B,), device=device)
                noise = torch.randn_like(act_seq)
                x_t   = scheduler.add_noise(act_seq, noise, t.cpu()).to(device)
                gc    = obs_encoder(obs_seq)
                pn    = noise_pred_net(x_t, t, gc)
                val_loss += F.mse_loss(pn, noise).item() * B

        val_loss /= n_val
        lr_sched.step()

        if epoch % 20 == 0 or epoch == 1:
            mark = " ★" if val_loss < best_val_loss else ""
            print(
                f"[{epoch:4d}/{args.epochs}] "
                f"train={train_loss:.5f}  val={val_loss:.5f}  "
                f"lr={lr_sched.get_last_lr()[0]:.2e}{mark}"
            )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_cnt  = 0
            torch.save(
                {
                    'epoch':            epoch,
                    'val_loss':         val_loss,
                    'obs_dim':          OBS_DIM,
                    'action_dim':       ACTION_DIM,
                    'obs_horizon':      args.obs_horizon,
                    'pred_horizon':     args.pred_horizon,
                    'diff_steps':       args.diff_steps,
                    'obs_encoder':      obs_encoder.state_dict(),
                    'noise_pred_net':   noise_pred_net.state_dict(),
                },
                os.path.join(args.out_dir, 'dp_best.pt'),
            )
        else:
            patience_cnt += 1
            if patience_cnt >= args.patience:
                print(f"[EARLY STOP] epoch={epoch}  patience={args.patience}")
                break

    print("=" * 65)
    print(f"[DONE] best val loss : {best_val_loss:.5f}")
    print(f"[DONE] 모델  : {args.out_dir}/dp_best.pt")
    print(f"[DONE] 정규화: {args.out_dir}/obs_norm.npz  act_norm.npz")
    print()
    print("실행 명령 예시:")
    print(f"  python3 diffusion_run.py --model {args.out_dir}/dp_best.pt \\")
    print(f"      --obs_norm {args.out_dir}/obs_norm.npz \\")
    print(f"      --act_norm {args.out_dir}/act_norm.npz \\")
    print( "      --target_angle 720.0 --dip_gain 0.5")


if __name__ == '__main__':
    train()
