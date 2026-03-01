#!/usr/bin/env python3
"""
TUMI Glove Gain Tunery: 손가락별 텍타일 gain 튜닝 실험용.

- 기본: 모든 관절 0
- ENABLE_THUMB/INDEX/MIDDLE 로 실험 대상 손가락 선택
- 손가락별 MCP/PIP/DIP gain 개별 설정 가능
"""

import rclpy
from rclpy.node import Node
import serial
import time
from kistar_hand_ros2.msg import HandTarget
from std_msgs.msg import Float32MultiArray

# 한 줄 데이터: 16 joint (int) + 21 tactile (float, 소수점 2자리)
NUM_JOINTS = 16
NUM_TACTILE = 21

# 실험 대상 손가락 ON/OFF (True=활성, False=비활성)
ENABLE_THUMB  = False
ENABLE_INDEX  = False
ENABLE_MIDDLE = True
ENABLE_RING   = False  # Ring 택타일 없음 -> Middle 과 동기화 시 사용

# 손가락별 gain (TUMI_Glove_Publisher.py 29-53 기준, 동일)
# Thumb (텍타일 0-6)
thumb_gain_ip = 5.0
thumb_gain_mcp = 5.0
thumb_gain_cmc_opposition = 2.5
# Index (텍타일 7-13)
index_gain_dip = 10.0
index_gain_pip = 10.0
index_gain_mcp_flexion = 5.0
# Middle (텍타일 14-20)
middle_gain_dip = 10.0
middle_gain_pip = 10.0
middle_gain_mcp_flexion = 5.0
# Ring (택타일 없음 -> Middle 과 동기화)
ring_gain_dip = 5.0
ring_gain_pip = 5.0
ring_gain_mcp_flexion = 2.5
TACTILE_PER_FINGER = 7  # Thumb 0-6, Index 7-13, Middle 14-20

# 로봇 핸드 16 joint 인덱스 (TUMI_Glove_Publisher.py 29-53 기준, 동일)
# 0-3: Thumb, 4-7: Index, 8-11: Middle, 12-15: Ring
joint_thumb_cmc_opposition, joint_thumb_cmc_abduction, joint_thumb_mcp, joint_thumb_ip = 0, 1, 2, 3
joint_index_mcp_abduction, joint_index_mcp_flexion, joint_index_pip, joint_index_dip = 4, 5, 6, 7
joint_middle_mcp_abduction, joint_middle_mcp_flexion, joint_middle_pip, joint_middle_dip = 8, 9, 10, 11
joint_ring_mcp_abduction, joint_ring_mcp_flexion, joint_ring_pip, joint_ring_dip = 12, 13, 14, 15

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
    return max(lo, min(hi, int(round(value))))


def parse_glove_line(line: str):
    """
    한 줄 파싱: "j0,j1,...,j15,p0.00,p1.00,...,p20.00"
    Returns: (joints[16], tactiles[21]) or (None, None)
    """
    parts = line.strip().split(',')
    if len(parts) != NUM_JOINTS + NUM_TACTILE:
        return None, None
    try:
        joints = [int(parts[i]) for i in range(NUM_JOINTS)]
        tactiles = [float(parts[NUM_JOINTS + i]) for i in range(NUM_TACTILE)]
        return joints, tactiles
    except (ValueError, IndexError):
        return None, None


def tactile_max(tactiles: list, start: int, count: int = TACTILE_PER_FINGER) -> float:
    """손가락별 촉각 최댓값 (가장 강한 압력 기준)"""
    s = tactiles[start : start + count]
    return max(s) if s else 0.0


class TUMIGloveGainTunery(Node):
    def __init__(self):
        super().__init__('tumi_glove_gain_tunery_node')
        self.publisher_ = self.create_publisher(HandTarget, '/hand/target/right', 10)
        self.tactile_pub_ = self.create_publisher(Float32MultiArray, '/glove/tactile', 10)

        # ROS 파라미터
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('enable_thumb', ENABLE_THUMB)
        self.declare_parameter('enable_index', ENABLE_INDEX)
        self.declare_parameter('enable_middle', ENABLE_MIDDLE)
        self.declare_parameter('enable_ring', ENABLE_RING)
        self.declare_parameter('publish_tactile', True)  # False 시 촉각 토픽 미발행 (히트맵 viz용)

        self.serial_port = self.get_parameter('port').get_parameter_value().string_value
        self.baudrate = self.get_parameter('baudrate').get_parameter_value().integer_value

        try:
            self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=0.1)
            self.ser.reset_input_buffer()
            time.sleep(2)
            self.ser.reset_input_buffer()
            self.get_logger().info(f'Serial connected: {self.serial_port}')
        except Exception as e:
            self.get_logger().error(f'Connection failed: {e}')
            raise

        self.timer = self.create_timer(0.01, self.timer_callback)

    def _compute_targets(self, joints: list, tactiles: list) -> list:
        """활성화된 손가락만 텍타일에 따라 눌림, 나머지 0. (TUMI_Glove_Publisher 기준)"""
        out = [0.0] * NUM_JOINTS

        if ENABLE_THUMB:
            t_max = tactile_max(tactiles, 0)
            out[joint_thumb_cmc_opposition] = 1000 * thumb_gain_cmc_opposition * (t_max / 1000000)
            out[joint_thumb_mcp] = 1000 * thumb_gain_mcp * (t_max / 1000000)
            out[joint_thumb_ip] = 1000 * thumb_gain_ip * (t_max / 1000000)

        if ENABLE_INDEX:
            i_max = tactile_max(tactiles, 7)
            out[joint_index_mcp_flexion] = 1000 * index_gain_mcp_flexion * (i_max / 1000000)
            out[joint_index_pip] = 1000 * index_gain_pip * (i_max / 1000000)
            out[joint_index_dip] = 1000 * index_gain_dip * (i_max / 1000000)

        if ENABLE_MIDDLE:
            m_max = tactile_max(tactiles, 14)
            out[joint_middle_mcp_flexion] = 1000 * middle_gain_mcp_flexion * (m_max / 1000000)
            out[joint_middle_pip] = 1000 * middle_gain_pip * (m_max / 1000000)
            out[joint_middle_dip] = 1000 * middle_gain_dip * (m_max / 1000000)

        if ENABLE_RING:
            # Ring 택타일 없음 -> Middle 과 동기화
            m_max = tactile_max(tactiles, 14)
            out[joint_ring_mcp_flexion] = 1000 * ring_gain_mcp_flexion * (m_max / 1000000)
            out[joint_ring_pip] = 1000 * ring_gain_pip * (m_max / 1000000)
            out[joint_ring_dip] = 1000 * ring_gain_dip * (m_max / 1000000)

        return [clamp_joint(i, out[i]) for i in range(NUM_JOINTS)]

    def timer_callback(self):
        try:
            if self.ser is None or not self.ser.is_open:
                return
            if self.ser.in_waiting > 500:
                self.ser.reset_input_buffer()
                self.get_logger().warn('Serial buffer overflow, clearing.')
        except (OSError, serial.SerialException) as e:
            self.get_logger().error(f'Serial error: {e}')
            return

        last_msg = None
        last_tactiles = None
        while self.ser.in_waiting > 0:
            try:
                raw_line = self.ser.readline()
                decoded = raw_line.decode('utf-8').strip()
                if not decoded:
                    continue
                joints, tactiles = parse_glove_line(decoded)
                if joints is None:
                    if decoded and not decoded.startswith('  ['):
                        self.get_logger().warn(f'Parse skip: {len(decoded.split(","))} fields')
                    continue
                targets = self._compute_targets(joints, tactiles)
                msg = HandTarget()
                msg.joint_targets = targets
                msg.movement_duration = 0.1
                msg.hand_id = 0
                last_msg = msg
                last_tactiles = tactiles
            except (UnicodeDecodeError, ValueError) as e:
                self.get_logger().debug(f'Parse error: {e}')
                continue

        if last_msg:
            self.publisher_.publish(last_msg)
        if last_tactiles is not None and self.get_parameter('publish_tactile').get_parameter_value().bool_value:
            tac_msg = Float32MultiArray()
            tac_msg.data = [float(v) for v in last_tactiles]
            self.tactile_pub_.publish(tac_msg)

    def destroy_node(self):
        if hasattr(self, 'ser') and self.ser and self.ser.is_open:
            self.ser.close()
            self.get_logger().info('Serial port closed.')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = TUMIGloveGainTunery()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard Interrupt')
    except Exception as e:
        node.get_logger().error(f'Error: {e}')
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()

#
# 실행: cd R_Franka_KISTAR_Hand && python3 TUMI_Glove_Gain_tunnery.py
# ENABLE_THUMB/INDEX/MIDDLE 로 실험 대상 선택, 손가락별 GAIN 상단에서 조정.
#
