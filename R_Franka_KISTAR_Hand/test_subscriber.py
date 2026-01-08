#!/usr/bin/env python3
"""간단한 subscriber 테스트"""

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from kistar_hand_ros2.msg import FrankaArmState

class TestSub(Node):
    def __init__(self):
        super().__init__('test_subscriber')
        
        # 여러 QoS 프로파일 시도
        self.sub = self.create_subscription(
            FrankaArmState,
            '/franka/arm_state/right',  # 절대 경로
            self.callback,
            qos_profile_sensor_data  # sensor data QoS 사용
        )
        self.get_logger().info('테스트 subscriber 시작!')
        self.get_logger().info('토픽: /franka/arm_state/right')
        self.count = 0
        
        # 타이머로 상태 체크
        self.timer = self.create_timer(1.0, self.check_status)
        
    def callback(self, msg):
        self.count += 1
        self.get_logger().info(f'✅ 수신 #{self.count}! joint[0]={msg.joint_positions[0]:.4f}')

    def check_status(self):
        self.get_logger().info(f'📊 지금까지 수신: {self.count}개')

def main():
    rclpy.init()
    node = TestSub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

