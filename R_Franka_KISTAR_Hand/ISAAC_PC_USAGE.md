# Isaac PC에서 ROS2 사용 가이드

## 📋 Hand와 Arm 동시 제어 방법

### 방법 1: Python 노드에서 함수 호출

`isaac_ros2_bridge.py`의 `send_both_targets()` 함수 사용:

```python
from kistar_hand_ros2.msg import FrankaArmTarget, HandTarget
import rclpy
from rclpy.node import Node

# 노드 생성 후
node = IsaacRos2Bridge()

# Arm + Hand 동시 전송
arm_joints = [0.5, -0.6, 0.7, -2.4, -0.02, 1.2, 0.2]  # 7개 관절 [rad]
hand_joints = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 
               1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]  # 16개 관절

node.send_both_targets(
    arm_id=0,                    # 0=Right, 1=Left
    arm_joint_targets=arm_joints,
    hand_id=0,                   # 0=Right, 1=Left
    hand_joint_targets=hand_joints,
    hand_duration=1.0            # Hand 이동 시간 [초]
)
```

### 방법 2: ros2 topic pub 명령어 (터미널)

**두 개의 토픽을 거의 동시에 전송:**

```bash
# 터미널 1: Arm target 전송
ros2 topic pub --once /franka/arm_target/right \
  kistar_hand_ros2/msg/FrankaArmTarget \
  "{joint_targets: [0.5, -0.6, 0.7, -2.4, -0.02, 1.2, 0.2], arm_id: 0}"

# 터미널 2: Hand target 전송 (거의 동시에 실행)
ros2 topic pub --once /hand/target/right \
  kistar_hand_ros2/msg/HandTarget \
  "{joint_targets: [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000], movement_duration: 1.0, hand_id: 0}"
```

**또는 한 줄로 (백그라운드 실행):**

```bash
# Arm과 Hand를 거의 동시에 전송
ros2 topic pub --once /franka/arm_target/right kistar_hand_ros2/msg/FrankaArmTarget \
  "{joint_targets: [0.5, -0.6, 0.7, -2.4, -0.02, 1.2, 0.2], arm_id: 0}" & \
ros2 topic pub --once /hand/target/right kistar_hand_ros2/msg/HandTarget \
  "{joint_targets: [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000], movement_duration: 1.0, hand_id: 0}"
```

### 방법 3: Python 스크립트로 동시 전송

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from kistar_hand_ros2.msg import FrankaArmTarget, HandTarget

class SimultaneousController(Node):
    def __init__(self):
        super().__init__('simultaneous_controller')
        
        # Publishers
        self.pub_arm = self.create_publisher(
            FrankaArmTarget, '/franka/arm_target/right', 10)
        self.pub_hand = self.create_publisher(
            HandTarget, '/hand/target/right', 10)
    
    def send_both(self):
        # Arm 메시지
        arm_msg = FrankaArmTarget()
        arm_msg.arm_id = 0
        arm_msg.joint_targets = [0.5, -0.6, 0.7, -2.4, -0.02, 1.2, 0.2]
        
        # Hand 메시지
        hand_msg = HandTarget()
        hand_msg.hand_id = 0
        hand_msg.joint_targets = [1000] * 16  # 모두 1000
        hand_msg.movement_duration = 1.0
        
        # 동시에 publish
        self.pub_arm.publish(arm_msg)
        self.pub_hand.publish(hand_msg)
        
        self.get_logger().info('✅ Arm + Hand 동시 전송 완료!')

def main():
    rclpy.init()
    node = SimultaneousController()
    node.send_both()
    rclpy.spin_once(node, timeout_sec=0.1)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

---

## 📌 중요 사항

1. **동시 전송**: 두 개의 `publish()` 호출을 연속으로 하면 거의 동시에 전송됩니다 (밀리초 단위 차이)

2. **토픽 분리**: Arm과 Hand는 별도의 토픽이므로 순서에 관계없이 전송 가능

3. **타이밍**: ROS2는 비동기 통신이므로 두 메시지가 거의 동시에 도착합니다

---

## 🔧 Isaac Sim에서 사용 예시

```python
# Isaac Sim Extension에서
from isaac_ros2_bridge import IsaacRos2Bridge

# 노드 생성
bridge = IsaacRos2Bridge()

# 시뮬레이션 루프에서
def on_step():
    # Arm + Hand 동시 제어
    arm_target = [0.5, -0.6, 0.7, -2.4, -0.02, 1.2, 0.2]
    hand_target = [1000] * 16
    
    bridge.send_both_targets(
        arm_id=0,
        arm_joint_targets=arm_target,
        hand_id=0,
        hand_joint_targets=hand_target,
        hand_duration=1.0
    )
```

---

*작성일: 2026-01-08*

