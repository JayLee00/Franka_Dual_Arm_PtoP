#!/usr/bin/env python3
"""
Isaac pc 에서 실행되는 pythob file 예제
Isaac ROS2 Bridge - 테스트용 노드

shm_ros2_bridge와 통신하여 데이터 송수신 테스트
나중에 Isaac Sim PC에서 실행할 노드의 템플릿

구조:
  franka, hand <-> shm <-> /shm_ros2_bridge <-> /isaac_ros2_bridge (이 노드)

역할:
  - arm_state, hand_state를 subscribe (로봇 상태 수신)
  - arm_target, hand_target을 publish (로봇 목표 전송)
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
import numpy as np
import math

# 메시지 타입 import
from kistar_hand_ros2.msg import FrankaArmState, FrankaArmTarget
from kistar_hand_ros2.msg import HandState, HandTarget


class IsaacRos2Bridge(Node):
    def __init__(self):
        super().__init__('isaac_ros2_bridge')
        
        self.get_logger().info('🚀 Isaac ROS2 Bridge 시작')
        
        # QoS 설정 (shm_ros2_bridge와 호환되도록)
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        # ============================================
        # Subscribers (로봇 상태 수신)
        # ============================================
        
        # Franka Arm State (오른쪽)
        self.sub_arm_state_R = self.create_subscription(
            FrankaArmState,
            '/franka/arm_state/right',
            self.arm_state_callback_R,
            qos
        )
        
        # Franka Arm State (왼쪽)
        self.sub_arm_state_L = self.create_subscription(
            FrankaArmState,
            '/franka/arm_state/left',
            self.arm_state_callback_L,
            qos
        )
        
        # Hand State (오른쪽)
        self.sub_hand_state_R = self.create_subscription(
            HandState,
            '/hand/state/right',
            self.hand_state_callback_R,
            qos
        )
        
        # Hand State (왼쪽)
        self.sub_hand_state_L = self.create_subscription(
            HandState,
            '/hand/state/left',
            self.hand_state_callback_L,
            qos
        )
        
        # ============================================
        # Publishers (로봇 목표 전송)
        # ============================================
        
        # Franka Arm Target
        self.pub_arm_target_R = self.create_publisher(
            FrankaArmTarget,
            '/franka/arm_target/right',
            qos
        )
        self.pub_arm_target_L = self.create_publisher(
            FrankaArmTarget,
            '/franka/arm_target/left',
            qos
        )
        
        # Hand Target
        self.pub_hand_target_R = self.create_publisher(
            HandTarget,
            '/hand/target/right',
            qos
        )
        self.pub_hand_target_L = self.create_publisher(
            HandTarget,
            '/hand/target/left',
            qos
        )
        
        # ============================================
        # 내부 상태 저장
        # ============================================
        self.arm_state_R = None
        self.arm_state_L = None
        self.hand_state_R = None
        self.hand_state_L = None
        
        self.receive_count = 0
        self.send_count = 0
        
        # ============================================
        # 타이머 (상태 출력 및 테스트 목표 전송)
        # ============================================
        
        # 상태 출력 타이머 (1Hz)
        self.print_timer = self.create_timer(1.0, self.print_status)
        
        # 테스트 목표 전송 타이머 (비활성화 상태, 필요시 활성화)
        # self.target_timer = self.create_timer(0.1, self.send_test_target)
        
        self.get_logger().info('✅ 모든 subscriber/publisher 초기화 완료')
        self.get_logger().info('📡 /shm_ros2_bridge와 통신 대기 중...')
    
    # ============================================
    # Callback 함수들 (상태 수신)
    # ============================================
    
    def arm_state_callback_R(self, msg: FrankaArmState):
        self.arm_state_R = msg
        self.receive_count += 1
        if self.receive_count % 100 == 1:  # 100번마다 한 번씩 출력
            self.get_logger().info(f'🔔 콜백 호출됨! joint[0]={msg.joint_positions[0]:.3f}')
    
    def arm_state_callback_L(self, msg: FrankaArmState):
        self.arm_state_L = msg
        self.receive_count += 1
    
    def hand_state_callback_R(self, msg: HandState):
        self.hand_state_R = msg
        self.receive_count += 1
    
    def hand_state_callback_L(self, msg: HandState):
        self.hand_state_L = msg
        self.receive_count += 1
    
    # ============================================
    # 상태 출력
    # ============================================
    
    def print_status(self):
        self.get_logger().info('=' * 60)
        self.get_logger().info(f'📊 수신 카운트: {self.receive_count}, 전송 카운트: {self.send_count}')
        
        # Franka Arm 상태 출력
        if self.arm_state_R is not None:
            pos = [f'{p:.3f}' for p in self.arm_state_R.joint_positions]
            self.get_logger().info(f'🦾 Franka R 관절 [rad]: [{", ".join(pos)}]')
            
            tq = [f'{t:.2f}' for t in self.arm_state_R.joint_torques]
            self.get_logger().info(f'   Franka R 토크 [Nm]: [{", ".join(tq)}]')
        else:
            self.get_logger().warn('⚠️  Franka R 상태: 수신 안됨')
        
        if self.arm_state_L is not None:
            pos = [f'{p:.3f}' for p in self.arm_state_L.joint_positions]
            self.get_logger().info(f'🦾 Franka L 관절 [rad]: [{", ".join(pos)}]')
        else:
            self.get_logger().warn('⚠️  Franka L 상태: 수신 안됨')
        
        # Hand 상태 출력
        if self.hand_state_R is not None:
            pos = list(self.hand_state_R.joint_positions[:5])  # 처음 5개만
            self.get_logger().info(f'✋ Hand R 관절 (처음 5개): {pos}')
        else:
            self.get_logger().warn('⚠️  Hand R 상태: 수신 안됨')
        
        if self.hand_state_L is not None:
            pos = list(self.hand_state_L.joint_positions[:5])
            self.get_logger().info(f'✋ Hand L 관절 (처음 5개): {pos}')
        else:
            self.get_logger().warn('⚠️  Hand L 상태: 수신 안됨')
    
    # ============================================
    # 목표 전송 함수들
    # ============================================
    
    def send_arm_target(self, arm_id: int, joint_targets: list):
        """
        Franka Arm 목표 전송
        
        Args:
            arm_id: 0=Right, 1=Left
            joint_targets: 7개의 관절 목표 [rad]
        """
        msg = FrankaArmTarget()
        msg.arm_id = arm_id
        msg.joint_targets = joint_targets
        
        if arm_id == 0:
            self.pub_arm_target_R.publish(msg)
        else:
            self.pub_arm_target_L.publish(msg)
        
        self.send_count += 1
        self.get_logger().info(f'📤 Arm Target 전송 (id={arm_id}): {[f"{t:.3f}" for t in joint_targets]}')
    
    def send_hand_target(self, hand_id: int, joint_targets: list, duration: float = 1.0):
        """
        Hand 목표 전송
        
        Args:
            hand_id: 0=Right, 1=Left
            joint_targets: 16개의 관절 목표
            duration: 이동 시간 [초]
        """
        msg = HandTarget()
        msg.hand_id = hand_id
        msg.joint_targets = joint_targets
        msg.movement_duration = duration
        
        if hand_id == 0:
            self.pub_hand_target_R.publish(msg)
        else:
            self.pub_hand_target_L.publish(msg)
        
        self.send_count += 1
        self.get_logger().info(f'📤 Hand Target 전송 (id={hand_id}): {joint_targets[:5]}...')
    
    def send_both_targets(self, arm_id: int, arm_joint_targets: list, 
                          hand_id: int, hand_joint_targets: list, 
                          hand_duration: float = 1.0):
        """
        Arm과 Hand를 동시에 목표 전송
        
        Args:
            arm_id: 0=Right, 1=Left
            arm_joint_targets: 7개의 Arm 관절 목표 [rad]
            hand_id: 0=Right, 1=Left
            hand_joint_targets: 16개의 Hand 관절 목표
            hand_duration: Hand 이동 시간 [초]
        """
        # Arm Target 메시지 생성 및 전송
        arm_msg = FrankaArmTarget()
        arm_msg.arm_id = arm_id
        arm_msg.joint_targets = arm_joint_targets
        
        # Hand Target 메시지 생성 및 전송
        hand_msg = HandTarget()
        hand_msg.hand_id = hand_id
        hand_msg.joint_targets = hand_joint_targets
        hand_msg.movement_duration = hand_duration
        
        # 동시에 publish (거의 동시에 전송됨)
        if arm_id == 0:
            self.pub_arm_target_R.publish(arm_msg)
        else:
            self.pub_arm_target_L.publish(arm_msg)
        
        if hand_id == 0:
            self.pub_hand_target_R.publish(hand_msg)
        else:
            self.pub_hand_target_L.publish(hand_msg)
        
        self.send_count += 2
        self.get_logger().info(f'📤 Arm + Hand 동시 전송 완료!')
        self.get_logger().info(f'   Arm (id={arm_id}): {[f"{t:.3f}" for t in arm_joint_targets]}')
        self.get_logger().info(f'   Hand (id={hand_id}): {hand_joint_targets[:5]}...')
    
    def send_test_target(self):
        """
        테스트용 목표 전송 (타이머에서 호출)
        현재 위치 기반으로 약간의 오프셋 추가
        """
        if self.arm_state_R is not None:
            # 현재 위치를 그대로 목표로 (안전)aac ROS2 Bridge - 테스트용 노드

shm_ros2_bridge와 통신하여 데이터 송수신 테스트
나중에 Isaac Sim PC에서 실행할 노드의 템플릿

구조:
  franka, hand <-> shm <-> /shm_ros2_bridge <-> /isaac_ros2_bridge (이 노드)

역할:
    rclpy.init(args=args)
    
    node = IsaacRos2Bridge()
    
    print()
    print('=' * 60)
    print('  Isaac ROS2 Bridge - 테스트 노드')
    print('=' * 60)
    print()
    print('  명령어:')
    print('    Ctrl+C : 종료')
    print()
    print('  rqt_graph에서 연결 확인 가능')
    print('=' * 60)
    print()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('👋 종료 요청됨')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

