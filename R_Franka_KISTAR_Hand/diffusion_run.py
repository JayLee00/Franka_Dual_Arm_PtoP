#!/usr/bin/env python3
"""
Low-D Diffusion Policy ROS2 실행기 — KISTAR Hand 전구 돌리기 태스크

═══════════════════════════════════════════════════════════════════════
  동작 흐름:
    1. 관찰 버퍼 유지: 최근 T_obs 스텝의 state(32차원) 저장
    2. ACTION_STEPS 마다 DDIM 추론 (10스텝, ~수ms)
       → pred_horizon(16) 스텝의 관절 타겟 시퀀스 생성
    3. ACTION_STEPS 개씩 순서대로 HandTarget 발행
    4. DIP 보정: target[DIP_idx] += 1000*dip_gain*(error/360)*tac_on

  DIP 관절: TUMI_Glove_Publisher.py 29-53 기준
    joint_thumb_ip, joint_index_dip, joint_middle_dip, joint_ring_dip (= 3, 7, 11, 15)
═══════════════════════════════════════════════════════════════════════

실행 예시:
  source install/setup.bash
  python3 diffusion_run.py \\
      --model      ./dp_model_2/dp_best.pt \\
      --obs_norm   ./dp_model_2/obs_norm.npz \\
      --act_norm   ./dp_model_2/act_norm.npz \\
      --target_angle 720.0 \\
      --dip_gain     0.5   \\
      --control_hz   50

  입력 속도 늦추기 (최대한 천천히):
    --control_hz 5          → 초당 5번만 타겟 전송 (기본 50)
    --movement_duration 0.5 → 한 타겟당 0.5초 동안 이동 (기본 0.1)
  스텝 없이 부드럽게 (인터폴레이션):
    --interp_steps 5        → 한 정책 타겟을 5틱에 걸쳐 현재 위치에서 선형 보간 (기본 5)
    예: python3 diffusion_run.py ... --interp_steps 10

구독:  hand/state/right (HandState), /bulb/angle (Float64)
발행:  hand/target/right (HandTarget), /dp/debug (Float64MultiArray)
"""

import argparse
import math
import sys
import threading
from collections import deque

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from std_msgs.msg import Float64, Float64MultiArray

try:
    from kistar_hand_ros2.msg import HandState, HandTarget
except ImportError:
    print("[ERROR] kistar_hand_ros2 메시지 import 실패.")
    print("        source install/setup.bash 후 재실행하세요.")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════
# 상수 (diffusion_train.py 와 동일하게 유지)
# ══════════════════════════════════════════════════════════════════════
TACTILE_THRESH    = 1000
FINGERS           = 4
TACTILE_PER_FINGER= 15
OBS_DIM           = 16 + 12 + 4   # 32
ACTION_DIM        = 16

OBS_HORIZON   = 2
PRED_HORIZON  = 16
ACTION_STEPS  = 8
DIFF_STEPS    = 100
INFER_STEPS   = 10

# 로봇 핸드 16 joint 인덱스 (TUMI_Glove_Publisher.py 29-53 기준)
# 0-3: Thumb, 4-7: Index, 8-11: Middle, 12-15: Ring
joint_thumb_cmc_opposition, joint_thumb_cmc_abduction, joint_thumb_mcp, joint_thumb_ip = 0, 1, 2, 3
joint_index_mcp_abduction, joint_index_mcp_flexion, joint_index_pip, joint_index_dip = 4, 5, 6, 7
joint_middle_mcp_abduction, joint_middle_mcp_flexion, joint_middle_pip, joint_middle_dip = 8, 9, 10, 11
joint_ring_mcp_abduction, joint_ring_mcp_flexion, joint_ring_pip, joint_ring_dip = 12, 13, 14, 15

DIP_JOINT_INDICES = [joint_thumb_ip, joint_index_dip, joint_middle_dip, joint_ring_dip]  # 3, 7, 11, 15

# 조인트별 클램프 (TUMI_Glove_Publisher.py 동일)
JOINT_LIMITS = []
for i in range(16):
    if i in (4, 8, 12):
        JOINT_LIMITS.append((-1000, 1000))
    elif i == 1:
        JOINT_LIMITS.append((-4096, 4096))
    else:
        JOINT_LIMITS.append((0, 4096))


# ══════════════════════════════════════════════════════════════════════
# DDPM 스케줄러 (학습과 동일)
# ══════════════════════════════════════════════════════════════════════
class DDPMScheduler:
    def __init__(self, num_steps: int = DIFF_STEPS):
        T = num_steps
        s = 0.008
        t = torch.arange(T + 1, dtype=torch.float64)
        f = torch.cos(((t / T + s) / (1.0 + s)) * math.pi / 2.0) ** 2
        alpha_bar = (f / f[0]).float()
        betas     = (1 - alpha_bar[1:] / alpha_bar[:-1]).clamp(max=0.999)
        alphas    = 1.0 - betas
        alpha_bar = torch.cumprod(alphas, dim=0)

        self.T         = T
        self.alpha_bar = alpha_bar
        self.sqrt_1m_ab= (1 - alpha_bar).sqrt()

    @torch.no_grad()
    def ddim_step(self, pred_noise, t_curr, t_prev, x_t):
        dev    = x_t.device
        ab     = self.alpha_bar[t_curr].to(dev)
        ab_prev = (self.alpha_bar[t_prev].to(dev)
                   if t_prev >= 0 else torch.tensor(1.0, device=dev))
        x0_pred = (x_t - (1 - ab).sqrt() * pred_noise) / ab.sqrt()
        x0_pred = x0_pred.clamp(-3.0, 3.0)
        return ab_prev.sqrt() * x0_pred + (1 - ab_prev).sqrt() * pred_noise

    def get_infer_timesteps(self, n_steps=INFER_STEPS):
        step = max(1, self.T // n_steps)
        return list(range(self.T - 1, -1, -step))[:n_steps]


# ══════════════════════════════════════════════════════════════════════
# 네트워크 (학습과 동일한 구조)
# ══════════════════════════════════════════════════════════════════════
class SinusoidalPosEmb(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, t):
        half = self.dim // 2
        freq = torch.exp(
            -math.log(10000)
            * torch.arange(half, device=t.device, dtype=torch.float32)
            / (half - 1)
        )
        emb = t.float()[:, None] * freq[None, :]
        return torch.cat([emb.sin(), emb.cos()], dim=-1)


class ConvResBlock(nn.Module):
    def __init__(self, in_ch, out_ch, cond_dim, kernel_size=3):
        super().__init__()
        pad = kernel_size // 2
        ng  = 8 if out_ch % 8 == 0 else (4 if out_ch % 4 == 0 else 1)
        self.conv1    = nn.Conv1d(in_ch,  out_ch, kernel_size, padding=pad)
        self.conv2    = nn.Conv1d(out_ch, out_ch, kernel_size, padding=pad)
        self.norm1    = nn.GroupNorm(ng, out_ch)
        self.norm2    = nn.GroupNorm(ng, out_ch)
        self.act      = nn.Mish()
        self.film     = nn.Linear(cond_dim, 2 * out_ch)
        self.shortcut = nn.Conv1d(in_ch, out_ch, 1) if in_ch != out_ch else nn.Identity()

    def forward(self, x, cond):
        scale, shift = self.film(cond).chunk(2, dim=-1)
        h = self.act(self.norm1(self.conv1(x)))
        h = h * (1 + scale[:, :, None]) + shift[:, :, None]
        h = self.act(self.norm2(self.conv2(h)))
        return h + self.shortcut(x)


class MLPObsEncoder(nn.Module):
    def __init__(self, obs_dim=OBS_DIM, obs_horizon=OBS_HORIZON, out_dim=256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim * obs_horizon, 256),
            nn.LayerNorm(256),
            nn.Mish(),
            nn.Linear(256, out_dim),
            nn.LayerNorm(out_dim),
            nn.Mish(),
        )

    def forward(self, obs):
        return self.net(obs.flatten(1))


class ConditionalUnet1D(nn.Module):
    def __init__(self, action_dim=ACTION_DIM, global_cond_dim=256,
                 time_emb_dim=128, channels=(64, 128, 256), kernel_size=3):
        super().__init__()
        self.time_mlp = nn.Sequential(
            SinusoidalPosEmb(time_emb_dim),
            nn.Linear(time_emb_dim, time_emb_dim * 4),
            nn.Mish(),
            nn.Linear(time_emb_dim * 4, time_emb_dim),
        )
        cond_dim = time_emb_dim + global_cond_dim

        self.stem = nn.Conv1d(action_dim, channels[0], kernel_size,
                              padding=kernel_size // 2)
        n_down  = len(channels) - 1
        enc_in  = [channels[0]] + list(channels[:-2])
        enc_out = list(channels[:-1])

        self.enc_blocks = nn.ModuleList([
            ConvResBlock(enc_in[i], enc_out[i], cond_dim, kernel_size)
            for i in range(n_down)
        ])
        self.enc_ds = nn.ModuleList([
            nn.Conv1d(enc_out[i], enc_out[i], 4, stride=2, padding=1)
            for i in range(n_down)
        ])
        self.mid_blocks = nn.ModuleList([
            ConvResBlock(channels[-2], channels[-1], cond_dim, kernel_size),
            ConvResBlock(channels[-1], channels[-1], cond_dim, kernel_size),
        ])
        dec_us_in = list(reversed(channels[1:]))
        dec_skip  = list(reversed(channels[:-1]))
        dec_out   = list(reversed(channels[:-1]))

        self.dec_us = nn.ModuleList([
            nn.ConvTranspose1d(dec_us_in[i], dec_us_in[i], 4, stride=2, padding=1)
            for i in range(n_down)
        ])
        self.dec_blocks = nn.ModuleList([
            ConvResBlock(dec_us_in[i] + dec_skip[i], dec_out[i], cond_dim, kernel_size)
            for i in range(n_down)
        ])
        self.head = nn.Conv1d(channels[0], action_dim, kernel_size,
                              padding=kernel_size // 2)

    def forward(self, noisy_actions, timestep, global_cond):
        x    = noisy_actions.permute(0, 2, 1)
        cond = torch.cat([self.time_mlp(timestep), global_cond], dim=-1)
        x    = self.stem(x)
        skips = []
        for block, ds in zip(self.enc_blocks, self.enc_ds):
            x = block(x, cond)
            skips.append(x)
            x = ds(x)
        for block in self.mid_blocks:
            x = block(x, cond)
        for us, block in zip(self.dec_us, self.dec_blocks):
            x    = us(x)
            skip = skips.pop()
            if x.shape[-1] != skip.shape[-1]:
                x = F.interpolate(x, size=skip.shape[-1], mode='nearest')
            x = torch.cat([x, skip], dim=1)
            x = block(x, cond)
        return self.head(x).permute(0, 2, 1)


# ══════════════════════════════════════════════════════════════════════
# 정규화 로더
# ══════════════════════════════════════════════════════════════════════
class Normalizer:
    def __init__(self, path: str):
        d = np.load(path)
        self.mean = d['mean'].astype(np.float32)
        self.std  = d['std'].astype(np.float32)

    def normalize(self, x: np.ndarray) -> np.ndarray:
        return (x - self.mean) / self.std

    def denormalize(self, x: np.ndarray) -> np.ndarray:
        return x * self.std + self.mean


# ══════════════════════════════════════════════════════════════════════
# 유틸
# ══════════════════════════════════════════════════════════════════════
def clamp_joint(idx: int, value: float) -> int:
    lo, hi = JOINT_LIMITS[idx]
    return int(max(lo, min(hi, round(value))))


# ══════════════════════════════════════════════════════════════════════
# ROS2 노드
# ══════════════════════════════════════════════════════════════════════
class DiffusionRunnerNode(Node):
    """Diffusion Policy 추론 + DIP 보정 + 액션 청킹 ROS2 노드."""

    def __init__(self, obs_encoder, noise_pred_net, scheduler,
                 obs_norm, act_norm, args):
        super().__init__('diffusion_runner')

        self.obs_encoder   = obs_encoder
        self.noise_pred_net= noise_pred_net
        self.scheduler     = scheduler
        self.obs_norm      = obs_norm
        self.act_norm      = act_norm
        self.args          = args
        self.device        = next(obs_encoder.parameters()).device

        self._lock         = threading.Lock()
        self._joint_pos    = np.zeros(16, dtype=np.float32)
        self._kinesthetic  = np.zeros(12, dtype=np.float32)
        self._tactile      = np.zeros(60, dtype=np.int16)
        self._bulb_angle   = 0.0
        self._hand_ready   = False

        # 관찰 버퍼 (최근 T_obs 스텝 유지)
        self._obs_buf = deque(maxlen=args.obs_horizon)
        # 액션 버퍼 (미실행 스텝들)
        self._act_buf = deque()
        # 인터폴레이션: 현재 향하고 있는 정책 타겟, 보간 스텝 인덱스
        self._interp_target = None   # (16,) float32 or None
        self._interp_index  = 0
        self._tick_cnt     = 0
        self._start_time   = self.get_clock().now()

        cb   = ReentrantCallbackGroup()
        side = args.hand_side

        self.create_subscription(HandState, f'hand/state/{side}',
                                 self._cb_hand_state, 10, callback_group=cb)
        self.create_subscription(Float64, '/bulb/angle',
                                 self._cb_bulb_angle, 10, callback_group=cb)

        self._target_pub = self.create_publisher(HandTarget, f'hand/target/{side}', 10)
        self._debug_pub  = self.create_publisher(Float64MultiArray, '/dp/debug', 10)

        self.create_timer(1.0 / args.control_hz, self._control_tick)

        self.get_logger().info("=" * 58)
        self.get_logger().info("  Diffusion Policy Runner 시작")
        self.get_logger().info(f"  hand_side    : {args.hand_side}")
        self.get_logger().info(f"  control_hz   : {args.control_hz} Hz  movement_duration : {args.movement_duration} s")
        self.get_logger().info(f"  target_angle : {args.target_angle:.1f} deg")
        self.get_logger().info(f"  dip_gain     : {args.dip_gain}")
        self.get_logger().info(f"  obs_horizon  : {args.obs_horizon}")
        self.get_logger().info(f"  pred_horizon : {args.pred_horizon}")
        self.get_logger().info(f"  action_steps : {args.action_steps}")
        self.get_logger().info(f"  interp_steps : {args.interp_steps} (선형 보간)")
        self.get_logger().info(f"  infer_steps  : {args.infer_steps} (DDIM)")
        self.get_logger().info("=" * 58)

    # ── 콜백 ──────────────────────────────────────────────────────────
    def _cb_hand_state(self, msg: HandState):
        with self._lock:
            self._joint_pos[:]   = np.array(msg.joint_positions,    dtype=np.float32)
            self._kinesthetic[:] = np.array(msg.kinesthetic_sensors, dtype=np.float32)
            self._tactile[:]     = np.array(msg.tactile_sensors,     dtype=np.int16)
            self._hand_ready     = True

    def _cb_bulb_angle(self, msg: Float64):
        with self._lock:
            self._bulb_angle = msg.data

    # ── 관찰 벡터 구성 ────────────────────────────────────────────────
    def _make_obs(self, joint_pos, kinesthetic, tactile) -> np.ndarray:
        """현재 센서값 → obs (OBS_DIM,) float32."""
        tac_bin = (
            tactile.reshape(FINGERS, TACTILE_PER_FINGER)
                   .max(axis=1) > TACTILE_THRESH
        ).astype(np.float32)
        return np.concatenate([joint_pos, kinesthetic, tac_bin])

    def _get_obs_seq(self) -> np.ndarray:
        """버퍼에서 (T_obs, OBS_DIM) 시퀀스 반환. 부족하면 첫 값으로 패딩."""
        buf = list(self._obs_buf)
        while len(buf) < self.args.obs_horizon:
            buf.insert(0, buf[0] if buf else np.zeros(OBS_DIM, dtype=np.float32))
        return np.stack(buf, axis=0)   # (T_obs, OBS_DIM)

    # ── DDIM 추론 ─────────────────────────────────────────────────────
    @torch.no_grad()
    def _infer(self, obs_seq: np.ndarray) -> np.ndarray:
        """obs_seq (T_obs, OBS_DIM) → action_seq (T_pred, ACTION_DIM) [정규화 해제]."""
        obs_n = self.obs_norm.normalize(obs_seq)                          # (T_obs, 32)
        obs_t = torch.from_numpy(obs_n).unsqueeze(0).to(self.device)     # (1, T_obs, 32)

        global_cond = self.obs_encoder(obs_t)                            # (1, 256)

        # 순수 가우시안 노이즈에서 시작
        x = torch.randn(1, self.args.pred_horizon, ACTION_DIM,
                        device=self.device)

        timesteps = self.scheduler.get_infer_timesteps(self.args.infer_steps)
        for i, t_curr in enumerate(timesteps):
            t_prev  = timesteps[i + 1] if i + 1 < len(timesteps) else -1
            t_batch = torch.tensor([t_curr], device=self.device)
            pred_noise = self.noise_pred_net(x, t_batch, global_cond)   # (1, T_pred, 16)
            x = self.scheduler.ddim_step(pred_noise, t_curr, t_prev, x)

        act_norm = x.squeeze(0).cpu().numpy()                           # (T_pred, 16)
        return self.act_norm.denormalize(act_norm)                      # (T_pred, 16)

    # ── 제어 틱 ───────────────────────────────────────────────────────
    def _control_tick(self):
        self._tick_cnt += 1

        with self._lock:
            if not self._hand_ready:
                elapsed = (self.get_clock().now() - self._start_time).nanoseconds / 1e9
                if self._tick_cnt % (self.args.control_hz * 3) == 0:
                    self.get_logger().warn(
                        f"⚠ hand/state/{self.args.hand_side} 미수신 ({elapsed:.0f}s 경과)"
                    )
                return

            joint_pos   = self._joint_pos.copy()
            kinesthetic = self._kinesthetic.copy()
            tactile     = self._tactile.copy()
            bulb_angle  = self._bulb_angle

        # ── 관찰 업데이트 ──────────────────────────────────────────
        obs = self._make_obs(joint_pos, kinesthetic, tactile)   # (32,)
        self._obs_buf.append(obs)

        # ── 재추론: 액션 버퍼가 비었을 때만 (인터폴 시 전체 시퀀스 사용) ──
        if not self._act_buf:
            obs_seq = self._get_obs_seq()                        # (T_obs, 32)
            try:
                action_seq = self._infer(obs_seq)                # (T_pred, 16)
            except Exception as e:
                self.get_logger().error(f"추론 오류: {e}")
                return
            for a in action_seq[:self.args.action_steps]:
                self._act_buf.append(a.copy())

        # ── 인터폴레이션: 다음 정책 타겟이 필요하면 pop ──
        interp_steps = max(1, self.args.interp_steps)
        if self._interp_target is None or self._interp_index >= interp_steps:
            if not self._act_buf:
                return
            self._interp_target = self._act_buf.popleft().astype(np.float32)  # (16,)
            self._interp_index  = 0

        # ── 현재 위치 → 정책 타겟 선형 보간 ───────────────────────
        t = min(1.0, (self._interp_index + 1) / interp_steps)
        target = joint_pos + (self._interp_target - joint_pos) * t   # (16,) float32
        self._interp_index += 1

        # ── DIP 보정 ──────────────────────────────────────────────
        tac_on    = float(tactile.max() > TACTILE_THRESH)
        error     = self.args.target_angle - bulb_angle
        dip_extra = 1000.0 * self.args.dip_gain * (error / 360.0) * tac_on
        dip_extra = float(np.clip(dip_extra, -self.args.dip_max, self.args.dip_max))

        for idx in DIP_JOINT_INDICES:
            target[idx] += dip_extra

        # ── 관절 한계 클램프 & 발행 ───────────────────────────────
        clamped = [clamp_joint(i, target[i]) for i in range(ACTION_DIM)]

        msg_out = HandTarget()
        msg_out.joint_targets     = clamped
        msg_out.movement_duration = self.args.movement_duration
        msg_out.hand_id           = 0     # Hand_R
        self._target_pub.publish(msg_out)

        # ── 디버그 발행 ───────────────────────────────────────────
        dbg = Float64MultiArray()
        dbg.data = [
            float(dip_extra),
            float(error),
            float(tac_on),
            float(bulb_angle),
            float(len(self._act_buf)),   # 남은 액션 수
        ]
        self._debug_pub.publish(dbg)

        # ── 콘솔 로그 (1초마다) ───────────────────────────────────
        if self._tick_cnt % self.args.control_hz == 0:
            delta     = [clamped[i] - int(joint_pos[i]) for i in range(ACTION_DIM)]
            max_delta = max(abs(d) for d in delta)
            self.get_logger().info(
                f"[TICK {self._tick_cnt:6d}] "
                f"bulb={bulb_angle:+6.1f}°  err={error:+6.1f}  "
                f"tac={'ON ' if tac_on else 'off'}  "
                f"dip={dip_extra:+5.0f}  "
                f"max_Δjoint={max_delta:5.0f}  "
                f"act_buf={len(self._act_buf)}  "
                f"tgt=[{','.join(str(v) for v in clamped[:4])}...]"
            )
            if max_delta < 5:
                self.get_logger().warn(
                    "  ↑ target ≈ current (Δ < 5). "
                    "모델 품질 또는 학습 데이터 확인 필요."
                )


# ══════════════════════════════════════════════════════════════════════
# main
# ══════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description='Diffusion Policy 실행기')
    parser.add_argument('--model',        default='./dp_model/dp_best.pt')
    parser.add_argument('--obs_norm',     default='./dp_model/obs_norm.npz')
    parser.add_argument('--act_norm',     default='./dp_model/act_norm.npz')
    parser.add_argument('--hand_side',    default='right')
    parser.add_argument('--control_hz',   type=int,   default=50,
                        help='초당 타겟 전송 횟수. 낮을수록 천천히 (예: 5)')
    parser.add_argument('--movement_duration', type=float, default=0.1,
                        help='한 타겟당 이동 시간(초). 클수록 손이 천천히 움직임 (예: 0.5)')
    parser.add_argument('--target_angle', type=float, default=720.0,
                        help='목표 전구 회전각 (deg)')
    parser.add_argument('--dip_gain',     type=float, default=0.5)
    parser.add_argument('--dip_max',      type=float, default=400.0)
    # 아키텍처 (학습 시 변경하지 않았다면 기본값 사용)
    parser.add_argument('--obs_horizon',  type=int, default=OBS_HORIZON)
    parser.add_argument('--pred_horizon', type=int, default=PRED_HORIZON)
    parser.add_argument('--action_steps', type=int, default=ACTION_STEPS,
                        help='추론마다 실행할 액션 스텝 수 (≤ pred_horizon)')
    parser.add_argument('--interp_steps', type=int, default=5,
                        help='한 정책 타겟을 몇 틱에 걸쳐 선형 보간할지 (1=스텝, 5~10=부드럽게)')
    parser.add_argument('--infer_steps',  type=int, default=INFER_STEPS,
                        help='DDIM 추론 스텝 수 (적을수록 빠름, 기본 10)')
    parser.add_argument('--diff_steps',   type=int, default=DIFF_STEPS)
    args, ros_args = parser.parse_known_args()

    # ── 파일 확인 ──
    missing = [p for p in [args.model, args.obs_norm, args.act_norm]
               if not __import__('os').path.exists(p)]
    if missing:
        print(f"[ERROR] 파일 없음: {missing}")
        print("  먼저 diffusion_train.py 로 학습 후 실행하세요.")
        return

    # ── 모델 로드 ──
    device = torch.device('cpu')   # 실시간 제어는 CPU로 충분
    ckpt   = torch.load(args.model, map_location=device, weights_only=True)

    # 체크포인트에서 하이퍼파라미터 복원 (있으면)
    if 'obs_horizon' in ckpt:
        args.obs_horizon  = ckpt['obs_horizon']
    if 'pred_horizon' in ckpt:
        args.pred_horizon = ckpt['pred_horizon']
    if 'diff_steps' in ckpt:
        args.diff_steps   = ckpt['diff_steps']

    obs_encoder = MLPObsEncoder(
        obs_dim=OBS_DIM, obs_horizon=args.obs_horizon, out_dim=256
    ).to(device)
    noise_pred_net = ConditionalUnet1D(
        action_dim=ACTION_DIM, global_cond_dim=256,
        time_emb_dim=128, channels=(64, 128, 256), kernel_size=3,
    ).to(device)

    obs_encoder.load_state_dict(ckpt['obs_encoder'])
    noise_pred_net.load_state_dict(ckpt['noise_pred_net'])
    obs_encoder.eval()
    noise_pred_net.eval()

    scheduler = DDPMScheduler(args.diff_steps)
    obs_norm  = Normalizer(args.obs_norm)
    act_norm  = Normalizer(args.act_norm)

    print(f"[MODEL] 로드: {args.model}  "
          f"epoch={ckpt.get('epoch','?')}  val_loss={ckpt.get('val_loss', float('nan')):.5f}")
    print(f"[NORM]  obs={args.obs_norm}  act={args.act_norm}")
    print(f"[INFER] DDIM {args.infer_steps}스텝  action_steps={args.action_steps}")

    # ── ROS2 ──
    rclpy.init(args=ros_args if ros_args else None)
    node = DiffusionRunnerNode(
        obs_encoder, noise_pred_net, scheduler, obs_norm, act_norm, args
    )
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Ctrl+C → 종료")
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
