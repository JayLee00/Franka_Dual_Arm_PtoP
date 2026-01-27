<<<<<<< HEAD
# 🤖 Franka Robot + ROS2 시스템 가이드

## 📌 시스템 구조

```
┌──────────────────────────────────────────────────────────────────────┐
│                           Robot PC                                   │
│                                                                      │
│  [Franka Robot] ◄──► [R_Franka_KISTAR_Hand] ◄──► [SHM]              │
│                                                   │                  │
│                                          [shm_ros2_bridge]           │
│                                                   │                  │
└───────────────────────────────────────────────────┼──────────────────┘
                                                    │
                                              ROS2 Topics
                                                    │
┌───────────────────────────────────────────────────┼──────────────────┐
│                          Isaac PC                 │                  │
│                                                   │                  │
│                                          [isaac_ros2_node]            │
│                                                   │                  │
│                                          [Isaac Sim 등]              │
└──────────────────────────────────────────────────────────────────────┘
```

---

# Part 1: Robot PC 실행 가이드

## 🚀 실행 순서 (3개 터미널)

### 터미널 1: 로봇 제어 프로그램


Terminal 1. 
sudo su 
shm 

Terminal 2. 
nd -> kistar bridge node turn on 


Useful commands:
rs -> ros turn on 

ethernet check.

enp1s0f0 -> Kistar_hand
enp1s0f3 -> Isaac_pc
realtech -> Franka

```bash
sudo su
cd /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/test
./R_Franka_KISTAR_Hand
```

**예상 출력:**
```
✅ Shared Memory 연결 성공
🔗 Connecting to Franka...
✅ Connected to Franka at 172.16.0.1
🚀 SHM Target 모드 시작
```

---

### 터미널 2: ROS2 브리지

ros2 환경설정
```bash
source /opt/ros/humble/setup.bash
source /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/install/setup.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DOMAIN_ID=9
export ROS_LOCALHOST_ONLY=0

ros2 topic echo /franka/arm_target/right
```

# 그 다음 명령어 실행
ros2 topic echo /franka/arm_target/right

```bash
cd /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand
source /opt/ros/humble/setup.bash
source install/setup.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DOMAIN_ID=9                  
export ROS_LOCALHOST_ONLY=0    
ros2 run kistar_hand_ros2 shm_ros2_bridge
```

**예상 출력:**
```
✅ Shared Memory 연결 성공
🚀 ROS2-SHM Bridge 노드 시작됨
```

---

### 터미널 3: Target 전송 테스트

```bash
cd /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand
source /opt/ros/humble/setup.bash
source install/setup.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DOMAIN_ID=9
export ROS_LOCALHOST_ONLY=0

python3 send_arm_target.py


ros2 run rqt_graph rqt_graph
```



**사용법:**
```
🚀 Arm Target Sender 시작!
==================================================
  1: 안전 포즈
  2: 움직임 1
  3: 움직임 2
  q: 종료
==================================================

포즈 번호 입력 (1/2/3/q): 1
📤 포즈 #1 (안전 포즈) 전송 중...
✅ 전송 완료!
```

→ 로봇이 해당 포즈로 이동합니다! 🤖

---
## ✅ 연결 테스트(ros2 topic pub 명령어 사용)

### Robot PC에서:
```bash
ros2 topic echo /franka/arm_state/right  # 상태 출력 확인
```

### Isaac PC에서:
```bash
# 상태 수신 테스트
ros2 topic echo /franka/arm_state/right

# 목표 전송 테스트 (Arm) 예시
ros2 topic pub --once /franka/arm_target/right \
  kistar_hand_ros2/msg/FrankaArmTarget \
  "{joint_targets: [0.5, -0.6, 0.7, -2.4, -0.02, 1.2, 0.2], arm_id: 0}"

[
  joint1:
  limit:
    lower:     -2.8973
    upper:      2.8973
    velocity:   2.1750
    effort:    87.0

joint2:
  limit:
    lower:     -1.7628
    upper:      1.7628
    velocity:   2.1750
    effort:    87.0

joint3:
  limit:
    lower:     -2.8973
    upper:      2.8973
    velocity:   2.1750
    effort:    87.0

joint4:
  limit:
    lower:     -3.0718
    upper:     -0.0698
    velocity:   2.1750
    effort:    87.0

joint5:
  limit:
    lower:     -2.8973
    upper:      2.8973
    velocity:   2.6100
    effort:    12.0

joint6:
  limit:
    lower:     -0.0175
    upper:      3.7525
    velocity:   2.6100
    effort:    12.0

joint7:
  limit:
    lower:     -2.8973
    upper:      2.8973
    velocity:   2.6100
    effort:    12.0
]

# 목표 전송 테스트 (Hand - 닫기) 예시
ros2 topic pub --once /hand/target/right \
  kistar_hand_ros2/msg/HandTarget \
  "{joint_targets: [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000], movement_duration: 1.0, hand_id: 0}"
```

ros2 topic pub --once /hand/target/right \
  kistar_hand_ros2/msg/HandTarget \
  "{joint_targets: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], movement_duration: 1.0, hand_id: 0}"
```


→ 로봇이 움직이면 연결 성공! 🎉


# Part 2: Isaac PC 연동 가이드

## 📡 ROS2 토픽

| 토픽 | 방향 | 메시지 타입 | 설명 |
|------|------|------------|------|
| `/franka/arm_state/right` | Robot → Isaac | FrankaArmState | 로봇 현재 상태 (100Hz) |
| `/franka/arm_target/right` | Isaac → Robot | FrankaArmTarget | 로봇 목표 위치 |

---

## 📨 메시지 구조

### FrankaArmState (로봇 상태 수신)
```
float64[7] joint_positions  # 현재 관절 위치 [rad]
float64[7] joint_torques    # 현재 관절 토크 [Nm]
uint8 arm_id                # 0=Right
```

### FrankaArmTarget (목표 위치 전송)
```
float64[7] joint_targets    # 목표 관절 위치 [rad]
uint8 arm_id                # 0=Right
```

---

## 🔧 Isaac PC 설정

### 1. 메시지 패키지 설치

Robot PC에서 다음 파일들을 복사:
```
msg/
├── FrankaArmState.msg
├── FrankaArmTarget.msg
├── HandState.msg
└── HandTarget.msg
```

또는 `install/` 폴더 전체를 복사해서 `source`

### 2. 네트워크 설정

**양쪽 PC에서 동일하게:**
```bash
export ROS_DOMAIN_ID=0
```

### 3. 연결 확인

```bash
# Isaac PC에서
ros2 topic list

# 다음 토픽이 보여야 함:
# /franka/arm_state/right
# /franka/arm_target/right
```





---

## 📝 요약

| Robot PC | Isaac PC |
|----------|----------|
| 로봇 제어 + shm_ros2_bridge 실행 | ROS2 노드 실행 |
| `/franka/arm_state/right` publish | subscribe |
| `/franka/arm_target/right` subscribe | publish |

**양쪽이 같은 네트워크 + 같은 ROS_DOMAIN_ID면 자동 연결!**

---

## 📂 파일 위치

### Robot PC 프로젝트 경로
```
/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/
```

### 주요 파일들

| 파일 | 경로 | 설명 |
|------|------|------|
| 로봇 제어 | `build/test/R_Franka_KISTAR_Hand` | 실행 파일 |
| ROS2 브리지 | `src/shm_ros2_bridge.cpp` | SHM ↔ ROS2 브리지 소스 |
| Target 전송 | `send_arm_target.py` | 목표 위치 전송 테스트 |
| SHM 모니터 | `monitor_shm.py` | SHM 데이터 모니터링 |
| Isaac 브리지 예제 | `isaac_ros2_bridge.py` | Isaac PC용 예제 코드 |

### 메시지 파일 (msg/)

```
msg/
├── FrankaArmState.msg      # 로봇 상태 메시지
├── FrankaArmTarget.msg     # 로봇 목표 메시지
├── HandState.msg           # 핸드 상태 메시지
└── HandTarget.msg          # 핸드 목표 메시지
```

### 빌드된 ROS2 패키지

```
install/kistar_hand_ros2/
├── lib/kistar_hand_ros2/shm_ros2_bridge    # 빌드된 실행 파일
└── share/kistar_hand_ros2/                  # 메시지 정의
```

---

## ⏱️ 통신 주파수

### 시스템 내부 주파수

| 구간 | 주파수 | 설명 |
|------|--------|------|
| Franka 제어 루프 | **1kHz** | libfranka 기본 (1ms) |
| SHM target 확인 | **1kHz** | R_Franka_KISTAR_Hand 루프 |
| SHM → ROS2 (state publish) | **100Hz** | shm_ros2_bridge 타이머 (10ms) |

### 네트워크 통신 (Isaac ↔ Robot)

| 환경 | 권장 주파수 | 비고 |
|------|------------|------|
| 같은 LAN (1Gbps) | **100-200Hz** | Real-time OS 사용 시 |
| 일반 네트워크 | **50-100Hz** | 안정성 우선 |
| WiFi | **30-50Hz** | 지연 변동 큼 |

### ⚠️ 현재 동작 방식

현재 코드는 **Point-to-Point 이동** 방식:
- Target이 0.01rad 이상 변할 때만 새로운 이동 시작
- 실시간 트래젝토리 추종이 아님

### 📊 주파수 확인 방법

```bash
# State publish 주파수 확인
ros2 topic hz /franka/arm_state/right

# Target 수신 주파수 확인
ros2 topic hz /franka/arm_target/right
```

### 🔧 State publish 주파수 변경

`src/shm_ros2_bridge.cpp`에서:
```cpp
// 현재: 100Hz (10ms)
timer_ = this->create_wall_timer(10ms, ...);

// 200Hz로 변경
timer_ = this->create_wall_timer(5ms, ...);
```

변경 후 재빌드:
```bash
colcon build
```

---

## 📞 정보

- Robot PC IP: `(확인 필요)`
- ROS2 버전: Humble
- ROS_DOMAIN_ID: 9
- RMW_IMPLEMENTATION: rmw_fastrtps_cpp
- 상태 publish 주파수: 100Hz (변경 가능)

---

*작성일: 2026-01-08*

=======
# Franka_Dual_Arm_PtoP
Franka and KISTAR_Hand controller setting with Ros2 and SHM
>>>>>>> cfd07a4f19c98e1707e4049e0999ed613e3c0043
