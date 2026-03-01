#!/usr/bin/env python3
"""
Franka 관절 각도(rad) 7개를 ROS2 토픽 /franka/arm_target/right 로 한 번 전송.

사용법:
  # 스크립트에 넣은 기본값 전송
  python3 send_franka_joints_once.py

  # 직접 7개 값 지정 (공백 구분)
  python3 send_franka_joints_once.py 0.7099 -0.07138 -0.667 -2.684 2.174 2.257 -0.972
"""

import re
import sys

# 사용자가 준 값 (7.099e-1 −7.138e-2 −6.670e-1 −2.684e+0 2.174e+0 2.257e+0 −9.720e-1)
DEFAULT_JOINTS = [
    7.099e-1,
    -7.138e-2,
    -6.670e-1,
    -2.684e+0,
    2.174e+0,
    2.257e+0,
    -9.720e-1,
]


def parse_joint_string(s: str):
    """공백/쉼표 없이 붙어 있는 과학적 표기 파싱. 예: 7.099e-1−7.138e-2..."""
    # 숫자 구분: e 다음에 +- 숫자가 끝난 뒤, 다음 숫자 시작 전까지
    # 패턴: (부호 선택)(숫자)(e(+-)숫자 선택) 으로 구분. −(U+2212) 도 부호로 처리
    s = s.replace("−", "-").replace(" ", "")
    parts = re.findall(r"-?\d+\.?\d*(?:e[+-]?\d+)?", s)
    out = []
    for p in parts:
        try:
            out.append(float(p))
        except ValueError:
            continue
    return out


def main():
    if len(sys.argv) >= 8:
        joints = [float(x) for x in sys.argv[1:8]]
    elif len(sys.argv) == 2:
        joints = parse_joint_string(sys.argv[1])
        if len(joints) != 7:
            print(f"❌ 파싱 결과 7개 아님: {len(joints)}개 → {joints}")
            sys.exit(1)
    else:
        joints = DEFAULT_JOINTS

    if len(joints) != 7:
        print(f"❌ 관절각은 7개여야 함. 현재 {len(joints)}개")
        sys.exit(1)

    try:
        import rclpy
        from rclpy.node import Node
        from kistar_hand_ros2.msg import FrankaArmTarget
    except ImportError:
        print("❌ rclpy 또는 kistar_hand_ros2 없음. source install/setup.bash 후 실행하세요.")
        sys.exit(1)

    rclpy.init()
    node = Node("send_franka_once")
    pub = node.create_publisher(FrankaArmTarget, "/franka/arm_target/right", 10)
    msg = FrankaArmTarget()
    msg.joint_targets = [float(q) for q in joints]
    msg.arm_id = 0

    # 구독자가 있을 때까지 잠시 대기
    import time
    time.sleep(0.3)
    pub.publish(msg)
    node.get_logger().info(
        f"📤 /franka/arm_target/right 전송: [{', '.join(f'{q:.4f}' for q in joints)}]"
    )
    time.sleep(0.2)
    node.destroy_node()
    rclpy.shutdown()
    print("✅ 전송 완료.")


if __name__ == "__main__":
    main()
