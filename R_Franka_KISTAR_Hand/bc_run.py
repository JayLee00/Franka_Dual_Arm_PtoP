#!/usr/bin/env python3
"""
BC 실행기 + DIP 추가 각도 생성기 — KISTAR Hand 전구 돌리기 태스크

═══════════════════════════════════════════════════════════════════════
  구조:
    1. BC 추론: state → MLP → angle (target_joint, 16)
    2. 각 손가락 접촉 시 DIP 추가: force_generator = dip_gain * tac_on
    3. Force_augmented_angle = angle + force_generator

  DIP 적용 관절: TUMI_Glove_Publisher.py 29-53 기준
    joint_thumb_ip, joint_index_dip, joint_middle_dip, joint_ring_dip (= 3, 7, 11, 15)

  dip_gain = (Bulb_vel_error / 10.0) * 1000
  Bulb_vel_error = 10 - 각도변화량 (10 deg/s - bulb angular velocity deg/s)
  tac_on = 손가락별 접촉 (thumb/index/middle 각각 15센서 max > TACTILE_THRESH)
  force_generator[i] = dip_gain * tac_on[i]  (각 DIP 관절별)

═══════════════════════════════════════════════════════════════════════

실행 예시:
  source install/setup.bash
  python3 bc_run.py \
      --model     ./bc_model/bc_best.pt \
      --state_norm  ./bc_model/state_norm.npz \
      --action_norm ./bc_model/action_norm.npz \
      --dip_max      400.0 \
      --control_hz   50

구독 토픽:
  hand/state/right    (HandState)      → joint_pos, kinesthetic, tactile
  /bulb/angle         (Float64)        → 현재 전구 누적 회전각 (deg)

발행 토픽:
  hand/target/right   (HandTarget)     → BC 출력 + DIP 보정 (Force_augmented_angle)
  /bc/dip_debug       (Float64MultiArray) → [dip_gain, bulb_vel_error, bulb_velocity, bulb_angle, tac_thumb, tac_index, tac_middle]

키보드:
  q → 종료
"""

import argparse
import threading
import sys

import numpy as np
import torch
import torch.nn as nn

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from std_msgs.msg import Float64MultiArray, Float64

try:
    from kistar_hand_ros2.msg import HandState, HandTarget
except ImportError:
    print("[ERROR] kistar_hand_ros2 메시지를 import 할 수 없습니다.")
    print("        source install/setup.bash 후 다시 실행하세요.")
    sys.exit(1)


# ── 상수 (TUMI_Glove_Publisher.py 29-53 기준, 동일) ─────────────────────────────
TACTILE_THRESH      = 1000
FINGERS             = 4
TACTILE_PER_FINGER  = 15
STATE_DIM           = 32   # 16 + 12 + 4
ACTION_DIM          = 16

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


def clamp_joint(idx: int, value: float) -> int:
    lo, hi = JOINT_LIMITS[idx]
    return int(max(lo, min(hi, round(value))))


# ── 모델 (학습과 동일한 구조) ─────────────────────────────────────────────────
class BCMLP(nn.Module):
    def __init__(self, state_dim=STATE_DIM, action_dim=ACTION_DIM, hidden=256, dropout=0.0):
        super().__init__()

        def block(in_d, out_d):
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

    def forward(self, x):
        return self.net(x)


# ── 정규화 ────────────────────────────────────────────────────────────────────
class Normalizer:
    def __init__(self, path: str):
        d = np.load(path)
        self.mean = d['mean'].astype(np.float32)
        self.std  = d['std'].astype(np.float32)

    def normalize(self, x: np.ndarray) -> np.ndarray:
        return (x - self.mean) / self.std

    def denormalize(self, x: np.ndarray) -> np.ndarray:
        return x * self.std + self.mean


# ── 유틸 ──────────────────────────────────────────────────────────────────────
def clamp_joint(idx: int, value: float) -> int:
    lo, hi = JOINT_LIMITS[idx]
    return int(max(lo, min(hi, round(value))))


# ── ROS2 노드 ─────────────────────────────────────────────────────────────────
class BCRunnerNode(Node):
    """BC 추론 + DIP 추가 각도 생성 ROS2 노드."""

    def __init__(self, model: nn.Module, s_norm: Normalizer, a_norm: Normalizer, args):
        super().__init__('bc_runner')
        self.model  = model
        self.s_norm = s_norm
        self.a_norm = a_norm
        self.args   = args

        self._lock = threading.Lock()

        # State buffers
        self._joint_pos   = np.zeros(16, dtype=np.float32)
        self._kinesthetic = np.zeros(12, dtype=np.float32)
        self._tactile     = np.zeros(60, dtype=np.int16)
        self._bulb_angle  = 0.0
        self._hand_ready  = False
        self._bulb_ready  = False
        self._prev_bulb_angle = None
        self._prev_bulb_time  = None

        cb = ReentrantCallbackGroup()
        side = args.hand_side

        # 구독
        self.create_subscription(
            HandState, f'hand/state/{side}',
            self._cb_hand_state, 10, callback_group=cb,
        )
        self.create_subscription(
            Float64, '/bulb/angle',
            self._cb_bulb_angle, 10, callback_group=cb,
        )

        # 발행
        self._target_pub = self.create_publisher(HandTarget, f'hand/target/{side}', 10)
        self._debug_pub  = self.create_publisher(Float64MultiArray, '/bc/dip_debug', 10)

        # 제어 타이머
        period = 1.0 / args.control_hz
        self.create_timer(period, self._control_tick)

        self._tick_cnt = 0
        self._start_time = self.get_clock().now()

        self.get_logger().info("=" * 55)
        self.get_logger().info("  BC Runner + DIP 제어기 시작")
        self.get_logger().info(f"  hand_side    : {args.hand_side}")
        self.get_logger().info(f"  control_hz   : {args.control_hz} Hz")
        self.get_logger().info(f"  dip_max      : {args.dip_max}")
        self.get_logger().info(f"  DIP joints   : {DIP_JOINT_INDICES}  (thumb_ip, index/middle/ring_dip)")
        self.get_logger().info("=" * 55)

    # ── 콜백 ──────────────────────────────────────────────────────────────────
    def _cb_hand_state(self, msg: HandState):
        with self._lock:
            self._joint_pos[:]   = np.array(msg.joint_positions,   dtype=np.float32)
            self._kinesthetic[:] = np.array(msg.kinesthetic_sensors, dtype=np.float32)
            self._tactile[:]     = np.array(msg.tactile_sensors,    dtype=np.int16)
            self._hand_ready     = True

    def _cb_bulb_angle(self, msg: Float64):
        with self._lock:
            self._bulb_angle = msg.data
            self._bulb_ready = True

    # ── 제어 틱 ───────────────────────────────────────────────────────────────
    def _control_tick(self):
        self._tick_cnt += 1

        with self._lock:
            if not self._hand_ready:
                # 3초 이상 대기 중이면 경고 출력
                elapsed = (self.get_clock().now() - self._start_time).nanoseconds / 1e9
                if self._tick_cnt % (self.args.control_hz * 3) == 0:
                    self.get_logger().warn(
                        f"⚠ hand/state/{self.args.hand_side} 미수신 ({elapsed:.0f}s 경과) — "
                        "shm_ros2_bridge 와 R_Franka_KISTAR_Hand 가 실행 중인지 확인하세요."
                    )
                return

            joint_pos   = self._joint_pos.copy()
            kinesthetic = self._kinesthetic.copy()
            tactile     = self._tactile.copy()
            bulb_angle  = self._bulb_angle

        # ── tactile binary (손가락별 4차원, state용 및 DIP force_generator용) ──
        tac_4d = (
            tactile.reshape(FINGERS, TACTILE_PER_FINGER)
                   .max(axis=1) > TACTILE_THRESH
        ).astype(np.float32)  # (4,)

        # ── BC 추론 ──
        state = np.concatenate([joint_pos, kinesthetic, tac_4d]).astype(np.float32)  # (32,)
        state_norm = self.s_norm.normalize(state)

        with torch.no_grad():
            x = torch.from_numpy(state_norm).unsqueeze(0)   # (1, 32)
            pred_norm = self.model(x).squeeze(0).numpy()    # (16,)

        target = self.a_norm.denormalize(pred_norm)   # (16,) float32 (정규화 해제) = angle

        # ── Bulb 각도 변화량(속도) 추정 ─────────────────────────────────────
        now = self.get_clock().now()
        now_sec = now.nanoseconds / 1e9
        bulb_velocity = 0.0   # deg/s
        if self._prev_bulb_angle is not None and self._prev_bulb_time is not None:
            dt = now_sec - self._prev_bulb_time
            if dt > 1e-6:   # dt가 유효할 때만
                bulb_velocity = (bulb_angle - self._prev_bulb_angle) / dt
        self._prev_bulb_angle = bulb_angle
        self._prev_bulb_time  = now_sec

        # Bulb_vel_error = 10 deg/s - 각도변화량
        bulb_vel_error = 10.0 - bulb_velocity
        bulb_vel_error = float(np.clip(bulb_vel_error, -10.0, 10.0))   # 범위 제한
        dip_gain = (bulb_vel_error / 10.0) * 1000.0

        # ── 각 손가락별 DIP 추가 각도: force_generator = dip_gain * tac_on ───
        # tac_4d: [thumb, index, middle, ring] — DIP는 thumb/index/middle만
        tac_on_dip = tac_4d[:3]   # (3,) — DIP 관절에 대응하는 손가락별 tac_on

        for i, idx in enumerate(DIP_JOINT_INDICES):
            force_gen = dip_gain * tac_on_dip[i]
            force_gen = float(np.clip(force_gen, -self.args.dip_max, self.args.dip_max))
            target[idx] += force_gen   # Force_augmented_angle = angle + force_generator

        # ── 관절 한계값 클램프 ──
        clamped = [clamp_joint(i, target[i]) for i in range(ACTION_DIM)]

        # ── HandTarget 발행 ──
        msg_out = HandTarget()
        msg_out.joint_targets     = clamped
        msg_out.movement_duration = 0.1   # TUMI와 동일 (0.0이면 일부 모션 로직이 무시할 수 있음)
        msg_out.hand_id           = 0     # Hand_R = 0 (shm.h 기준)
        self._target_pub.publish(msg_out)

        # ── 디버그 퍼블리시 ──
        debug_msg = Float64MultiArray()
        debug_msg.data = [
            float(dip_gain),       # dip_gain (Bulb_vel_error 기반)
            float(bulb_vel_error), # Bulb_vel_error
            float(bulb_velocity),  # bulb angular velocity (deg/s)
            float(bulb_angle),     # 현재 전구 각도 (deg)
        ] + [float(tac_on_dip[i]) for i in range(3)]  # tac_on [thumb, index, middle]
        self._debug_pub.publish(debug_msg)

        # ── 콘솔 로그 (1초마다) ──
        if self._tick_cnt % self.args.control_hz == 0:
            delta = [clamped[i] - int(joint_pos[i]) for i in range(ACTION_DIM)]
            max_delta = max(abs(d) for d in delta)
            tac_str = f"tac=[{','.join('1' if t else '0' for t in tac_on_dip)}]"
            self.get_logger().info(
                f"[TICK {self._tick_cnt:6d}] "
                f"bulb={bulb_angle:+6.1f}deg  vel={bulb_velocity:+5.2f}deg/s  "
                f"err={bulb_vel_error:+5.2f}  dip_gain={dip_gain:+6.0f}  "
                f"{tac_str}  max_Δjoint={max_delta:5.0f}  "
                f"target=[{','.join(str(v) for v in clamped[:6])}...]"
            )
            if max_delta < 5:
                self.get_logger().warn(
                    "  ↑ target ≈ current (최대 변화량 < 5). "
                    "학습 데이터가 부족하거나 모델이 평균값만 출력 중일 수 있습니다."
                )


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='BC 실행기 + DIP 추가 각도 생성기')
    parser.add_argument('--model',        default='./bc_model/bc_best.pt',
                        help='학습된 모델 경로')
    parser.add_argument('--state_norm',   default='./bc_model/state_norm.npz',
                        help='state 정규화 파라미터')
    parser.add_argument('--action_norm',  default='./bc_model/action_norm.npz',
                        help='action 정규화 파라미터')
    parser.add_argument('--hand_side',    default='right',
                        help='핸드 측 (right / left)')
    parser.add_argument('--control_hz',   type=int,   default=50,
                        help='제어 주파수 (Hz, 권장 50~100)')
    parser.add_argument('--dip_max',      type=float, default=400.0,
                        help='force_generator 클램프 절댓값')
    args, ros_args = parser.parse_known_args()

    # ── 모델 로드 ──
    if not all(map(lambda p: __import__('os').path.exists(p),
                   [args.model, args.state_norm, args.action_norm])):
        missing = [p for p in [args.model, args.state_norm, args.action_norm]
                   if not __import__('os').path.exists(p)]
        print(f"[ERROR] 파일 없음: {missing}")
        print("  먼저 bc_train.py로 학습 후 실행하세요.")
        return

    ckpt = torch.load(args.model, map_location='cpu', weights_only=True)
    model = BCMLP(
        state_dim=ckpt.get('state_dim',  STATE_DIM),
        action_dim=ckpt.get('action_dim', ACTION_DIM),
        hidden=ckpt.get('hidden', 256),
        dropout=0.0,   # 추론 시 dropout 비활성
    )
    model.load_state_dict(ckpt['model_state'])
    model.eval()
    print(
        f"[MODEL] 로드 완료: {args.model}  "
        f"(epoch={ckpt.get('epoch','?')}  val_loss={ckpt.get('val_loss', float('nan')):.5f})"
    )

    s_norm = Normalizer(args.state_norm)
    a_norm = Normalizer(args.action_norm)
    print(f"[NORM]  state_norm={args.state_norm}  action_norm={args.action_norm}")

    # ── ROS2 ──
    rclpy.init(args=ros_args if ros_args else None)
    node = BCRunnerNode(model, s_norm, a_norm, args)

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
