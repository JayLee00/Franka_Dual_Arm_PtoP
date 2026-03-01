#!/usr/bin/env python3
"""
HDF5 Data Recorder for KISTAR Hand + Glove + Bulb rotation.

ROS2 토픽을 구독하여 전구 돌리기 태스크 데이터를
robomimic 호환 HDF5 형식으로 저장합니다.

수집 데이터:
  - Real_hand_joint_pos      (N, 16) int16   로봇 핸드 관절 현재 위치
  - Real_hand_current        (N, 16) int16   모터 전류
  - Real_hand_kinesthetic    (N, 12) int16   역감 센서 (4×3)
  - Real_hand_tactile        (N, 60) int16   촉각 센서 (4×15)
  - Real_hand_target         (N, 16) int16   핸드 타겟 명령 (게인 적용됨)
  - Real_glove_encoder       (N, 16) int16   글러브 생 엔코더
  - Real_glove_tactile       (N, 21) float32 글러브 촉각 센서
  - Real_franka_joint_pos    (N, 7)  float64 프랑카 관절 위치 (7축)
  - Real_bulb_angle          (N,)    float64 로봇 전구 누적 회전각 (deg)
  - Real_human_bulb_angle    (N,)    float64 사람 전구 누적 회전각 (deg)
  - Real_timestamps          (N,)    float64 상대 타임스탬프(초)

실행:
  python3 HDF5_data_recorder.py [--ros-args -p record_hz:=100 ...]

키보드:
  Enter  → 녹화 토글 (시작 ↔ 저장)
  d      → 현재 에피소드 버림
  q      → 저장 후 종료

파일명: YYYY_MM_DD_HH_MM.hdf5
"""

import os
import sys
import json
import time
import threading
from datetime import datetime

import h5py
import numpy as np
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import Empty, Float32MultiArray, Int16MultiArray, Float64

try:
    from kistar_hand_ros2.msg import HandState, HandTarget, FrankaArmState
except ImportError:
    print("[WARN] kistar_hand_ros2 메시지를 import 할 수 없습니다.")
    print("       source install/setup.bash 후 다시 실행해 주세요.")
    sys.exit(1)


class HDF5DataRecorder(Node):

    HAND_DOF = 16
    KIN_DIM = 12
    TAC_DIM = 60
    GLOVE_TAC_DIM = 21
    ARM_DOF = 7

    def __init__(self):
        super().__init__('hdf5_data_recorder')

        # ── ROS 파라미터 ──
        self.declare_parameter('record_hz', 100)
        self.declare_parameter('max_demos', 10)
        self.declare_parameter('output_dir', './logs/hdf5_recordings')
        self.declare_parameter('hand_side', 'right')

        self.record_hz = self.get_parameter('record_hz').value
        self.max_demos = self.get_parameter('max_demos').value
        self.output_dir = self.get_parameter('output_dir').value
        self.hand_side = self.get_parameter('hand_side').value

        os.makedirs(self.output_dir, exist_ok=True)

        # ── 최신 수신 데이터 버퍼 (락 보호) ──
        self._lock = threading.Lock()
        self._hand_joint_pos = np.zeros(self.HAND_DOF, dtype=np.int16)
        self._hand_current = np.zeros(self.HAND_DOF, dtype=np.int16)
        self._hand_kinesthetic = np.zeros(self.KIN_DIM, dtype=np.int16)
        self._hand_tactile = np.zeros(self.TAC_DIM, dtype=np.int16)
        self._hand_target = np.zeros(self.HAND_DOF, dtype=np.int16)
        self._glove_encoder = np.zeros(self.HAND_DOF, dtype=np.int16)
        self._glove_tactile = np.zeros(self.GLOVE_TAC_DIM, dtype=np.float32)
        self._franka_joint_pos = np.zeros(self.ARM_DOF, dtype=np.float64)
        self._bulb_angle = 0.0
        self._human_bulb_angle = 0.0

        self._received_flags = {
            'hand_state': False,
            'hand_target': False,
            'glove_encoder': False,
            'glove_tactile': False,
            'franka_arm': False,
            'bulb_angle': False,
            'human_bulb_angle': False,
        }

        # ── ROS2 구독자 (ReentrantCallbackGroup → 타이머와 병렬 실행) ──
        sub_cb = ReentrantCallbackGroup()
        side = self.hand_side
        self.create_subscription(
            HandState, f'hand/state/{side}', self._cb_hand_state, 10,
            callback_group=sub_cb)
        self.create_subscription(
            HandTarget, f'hand/target/{side}', self._cb_hand_target, 10,
            callback_group=sub_cb)
        self.create_subscription(
            Int16MultiArray, '/glove/encoder', self._cb_glove_encoder, 10,
            callback_group=sub_cb)
        self.create_subscription(
            Float32MultiArray, '/glove/tactile', self._cb_glove_tactile, 10,
            callback_group=sub_cb)
        self.create_subscription(
            FrankaArmState, f'franka/arm_state/{side}', self._cb_franka_arm, 10,
            callback_group=sub_cb)
        self.create_subscription(
            Float64, '/bulb/angle', self._cb_bulb_angle, 10,
            callback_group=sub_cb)
        self.create_subscription(
            Float64, '/bulb/human_angle', self._cb_human_bulb_angle, 10,
            callback_group=sub_cb)
        self._bulb_reset_pub = self.create_publisher(Empty, '/bulb/reset', 1)

        # ── HDF5 파일 준비 ──
        ts = datetime.now().strftime('%Y_%m_%d_%H_%M')
        fname = f'{ts}.hdf5'
        self._hdf5_path = os.path.join(self.output_dir, fname)
        self._h5file = h5py.File(self._hdf5_path, 'w')
        self._h5data = self._h5file.create_group('data')
        self._h5data.attrs['total'] = 0
        self._h5data.attrs['env_args'] = json.dumps({
            'env_name': 'kistar_hand_bulb_rotation',
            'type': 2,
            'env_kwargs': {
                'hand_side': self.hand_side,
                'record_hz': self.record_hz,
            },
        })

        # ── 에피소드 버퍼 ──
        self._episode_buf = self._new_episode_buf()
        self._demo_count = 0
        self._recording = False
        self._t0 = 0.0
        self._bulb_angle_offset = None
        self._human_bulb_angle_offset = None

        # ── 녹화 타이머 ──
        period = 1.0 / self.record_hz
        self._rec_timer = self.create_timer(period, self._record_tick)

        # ── 키보드 입력 스레드 ──
        self._quit_event = threading.Event()
        self._kb_thread = threading.Thread(target=self._keyboard_loop, daemon=True)
        self._kb_thread.start()

        self.get_logger().info('=' * 50)
        self.get_logger().info(f'  HDF5 Data Recorder  (전구 돌리기)')
        self.get_logger().info(f'  파일: {self._hdf5_path}')
        self.get_logger().info(f'  Hz : {self.record_hz}  |  핸드: {self.hand_side}')
        self.get_logger().info(f'')
        self.get_logger().info(f'  [Enter] 녹화 시작 / 저장')
        self.get_logger().info(f'  [d]     현재 에피소드 버림')
        self.get_logger().info(f'  [q]     저장 후 종료')
        self.get_logger().info('=' * 50)

    # ──────────────────── 콜백 ────────────────────

    def _cb_hand_state(self, msg: HandState):
        with self._lock:
            self._hand_joint_pos[:] = msg.joint_positions
            self._hand_current[:] = msg.motor_current
            self._hand_kinesthetic[:] = msg.kinesthetic_sensors
            self._hand_tactile[:] = msg.tactile_sensors
            self._received_flags['hand_state'] = True

    def _cb_hand_target(self, msg: HandTarget):
        with self._lock:
            self._hand_target[:] = msg.joint_targets
            self._received_flags['hand_target'] = True

    def _cb_glove_encoder(self, msg: Int16MultiArray):
        with self._lock:
            n = min(len(msg.data), self.HAND_DOF)
            self._glove_encoder[:n] = msg.data[:n]
            self._received_flags['glove_encoder'] = True

    def _cb_glove_tactile(self, msg: Float32MultiArray):
        with self._lock:
            n = min(len(msg.data), self.GLOVE_TAC_DIM)
            self._glove_tactile[:n] = msg.data[:n]
            self._received_flags['glove_tactile'] = True

    def _cb_franka_arm(self, msg: FrankaArmState):
        with self._lock:
            self._franka_joint_pos[:] = msg.joint_positions
            self._received_flags['franka_arm'] = True

    def _cb_bulb_angle(self, msg: Float64):
        with self._lock:
            self._bulb_angle = msg.data
            self._received_flags['bulb_angle'] = True

    def _cb_human_bulb_angle(self, msg: Float64):
        with self._lock:
            self._human_bulb_angle = msg.data
            self._received_flags['human_bulb_angle'] = True

    # ──────────────────── 에피소드 버퍼 ────────────────────

    @staticmethod
    def _new_episode_buf():
        return {
            'Real_hand_joint_pos': [],
            'Real_hand_current': [],
            'Real_hand_kinesthetic': [],
            'Real_hand_tactile': [],
            'Real_hand_target': [],
            'Real_glove_encoder': [],
            'Real_glove_tactile': [],
            'Real_franka_joint_pos': [],
            'Real_bulb_angle': [],
            'Real_human_bulb_angle': [],
            'Real_timestamps': [],
        }

    # ──────────────────── 녹화 틱 ────────────────────

    def _record_tick(self):
        if not self._recording:
            return

        with self._lock:
            bulb_rel = self._bulb_angle - (self._bulb_angle_offset or 0.0)
            human_bulb_rel = self._human_bulb_angle - (self._human_bulb_angle_offset or 0.0)
            self._episode_buf['Real_hand_joint_pos'].append(self._hand_joint_pos.copy())
            self._episode_buf['Real_hand_current'].append(self._hand_current.copy())
            self._episode_buf['Real_hand_kinesthetic'].append(self._hand_kinesthetic.copy())
            self._episode_buf['Real_hand_tactile'].append(self._hand_tactile.copy())
            self._episode_buf['Real_hand_target'].append(self._hand_target.copy())
            self._episode_buf['Real_glove_encoder'].append(self._glove_encoder.copy())
            self._episode_buf['Real_glove_tactile'].append(self._glove_tactile.copy())
            self._episode_buf['Real_franka_joint_pos'].append(self._franka_joint_pos.copy())
            self._episode_buf['Real_bulb_angle'].append(bulb_rel)
            self._episode_buf['Real_human_bulb_angle'].append(human_bulb_rel)
            self._episode_buf['Real_timestamps'].append(time.time() - self._t0)

        n = len(self._episode_buf['Real_timestamps'])
        if n % (self.record_hz * 2) == 0:
            self.get_logger().info(
                f'  ● REC  {n} samples ({n / self.record_hz:.1f}s)  '
                f'robot_bulb={bulb_rel:.1f}deg  human_bulb={human_bulb_rel:.1f}deg')

    # ──────────────────── 에피소드 저장 ────────────────────

    def _save_episode(self):
        n_samples = len(self._episode_buf['Real_timestamps'])
        if n_samples == 0:
            self.get_logger().warn('빈 에피소드 - 저장 건너뜀')
            return False

        grp = self._h5data.create_group(f'demo_{self._demo_count}')
        grp.attrs['num_samples'] = n_samples

        for key, buf in self._episode_buf.items():
            arr = np.array(buf)
            grp.create_dataset(key, data=arr, compression='gzip', compression_opts=4)

        self._h5data.attrs['total'] += n_samples
        self._h5file.flush()
        self._demo_count += 1

        dur = self._episode_buf['Real_timestamps'][-1]
        self.get_logger().info(
            f'>>> demo_{self._demo_count - 1} 저장 완료: '
            f'{n_samples} samples, {dur:.1f}s  '
            f'({self._demo_count}/{self.max_demos})')
        return True

    # ──────────────────── 키보드 루프 ────────────────────

    def _keyboard_loop(self):
        while not self._quit_event.is_set():
            try:
                cmd = input().strip().lower()
            except EOFError:
                break

            if cmd == 'q':
                self.get_logger().info('종료 명령 수신')
                if self._recording and len(self._episode_buf['Real_timestamps']) > 0:
                    self._recording = False
                    self._save_episode()
                self._quit_event.set()
                rclpy.shutdown()
                break

            elif cmd == 'd':
                if self._recording:
                    n = len(self._episode_buf['Real_timestamps'])
                    self._recording = False
                    self._episode_buf = self._new_episode_buf()
                    self.get_logger().info(f'  ✕ 에피소드 버림 ({n} samples 삭제)')
                else:
                    self.get_logger().info('  녹화 중이 아닙니다.')

            elif cmd == '':
                if not self._recording:
                    self._start_recording()
                else:
                    self._stop_and_save()

            if self._demo_count >= self.max_demos:
                self._rotate_file()

    def _start_recording(self):
        self._bulb_reset_pub.publish(Empty())  # 양쪽 전구 각도 0으로 리셋 (트래커가 /bulb/reset 수신)
        with self._lock:
            self._bulb_angle = 0.0
            self._human_bulb_angle = 0.0
        self._bulb_angle_offset = 0.0
        self._human_bulb_angle_offset = 0.0
        self._print_topic_status()
        with self._lock:
            if not self._received_flags.get('bulb_angle', False):
                self.get_logger().warn(
                    '⚠ /bulb/angle 미수신 — Bulb_rotation_tracker.py --ros2 실행 확인')
            if not self._received_flags.get('human_bulb_angle', False):
                self.get_logger().warn(
                    '⚠ /bulb/human_angle 미수신 — 사람 전구 태그(ID6) 확인')
        self._episode_buf = self._new_episode_buf()
        self._t0 = time.time()
        self._recording = True
        self.get_logger().info(f'● 녹화 시작  (episode {self._demo_count}) — 전구 각도 0 기준')

    def _stop_and_save(self):
        self._recording = False
        self._save_episode()
        self._episode_buf = self._new_episode_buf()

    def _print_topic_status(self):
        with self._lock:
            flags = dict(self._received_flags)
        parts = []
        for k, v in flags.items():
            mark = 'OK' if v else '--'
            parts.append(f'{k}:{mark}')
        self.get_logger().info(f'  토픽: {" | ".join(parts)}')

    # ──────────────────── 파일 로테이션 ────────────────────

    def _rotate_file(self):
        """10개 에피소드 차면 현재 파일 닫고 새 파일 시작."""
        self._h5file.close()
        self.get_logger().info(
            f'=== 파일 완료: {self._hdf5_path} '
            f'({self._demo_count} episodes) ===')

        self._demo_count = 0
        self._file_count = getattr(self, '_file_count', 0) + 1
        ts = datetime.now().strftime('%Y_%m_%d_%H_%M')
        fname = f'{ts}_{self._file_count:02d}.hdf5'
        self._hdf5_path = os.path.join(self.output_dir, fname)
        self._h5file = h5py.File(self._hdf5_path, 'w')
        self._h5data = self._h5file.create_group('data')
        self._h5data.attrs['total'] = 0
        self._h5data.attrs['env_args'] = json.dumps({
            'env_name': 'kistar_hand_bulb_rotation',
            'type': 2,
            'env_kwargs': {
                'hand_side': self.hand_side,
                'record_hz': self.record_hz,
            },
        })
        self.get_logger().info(f'=== 새 파일: {self._hdf5_path} ===')

    # ──────────────────── 종료 ────────────────────

    def destroy_node(self):
        if self._recording:
            self._recording = False
            self._save_episode()
        if self._h5file:
            self._h5file.close()
            self.get_logger().info(f'HDF5 닫힘: {self._hdf5_path}')
            self.get_logger().info(
                f'총 {self._demo_count}개 에피소드, '
                f'{self._h5data.attrs["total"]} samples')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = HDF5DataRecorder()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info('Ctrl+C → 저장 후 종료')
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
