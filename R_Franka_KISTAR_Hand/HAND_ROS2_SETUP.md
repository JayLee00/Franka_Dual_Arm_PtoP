# Hand ROS2 연결 가이드

## 📋 작업 순서

### ✅ 1단계: EtherCAT 스레드 활성화 (완료)

`test/R_Franka_KISTAR_Hand.cpp`에서 EtherCAT 스레드 주석 해제 완료.

### ✅ 2단계: ROS2 → SHM (완료)

`src/shm_ros2_bridge.cpp`의 `handTargetCallback_R`이 이미 구현되어 있음:
- `/hand/target/right` 토픽 수신
- SHM의 `Hand_j_tar[Hand_R]`에 쓰기
- `Hand_CMD_Status[Hand_R] = true` 설정
- `hand_movement_duration[Hand_R]` 설정

### ✅ 3단계: SHM → EtherCAT (완료)

`include/kistar_hand/Hand_Arm_Setting.h`의 `ecatthread`에서:
- SHM의 `Hand_j_tar[Hand_R]` 읽기
- EtherCAT의 `JOINT_TARGET`로 전송

### 🔨 4단계: 빌드

```bash
cd /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand
mkdir -p build && cd build
cmake ..
make -j$(nproc)
```

### 🚀 5단계: 실행

**터미널 1: 로봇 + Hand 제어**
```bash
cd /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/test
sudo ./R_Franka_KISTAR_Hand
```

**터미널 2: ROS2 브리지**
```bash
cd /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand
source /opt/ros/humble/setup.bash
source install/setup.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DOMAIN_ID=9
export ROS_LOCALHOST_ONLY=0
ros2 run kistar_hand_ros2 shm_ros2_bridge
```

### 🧪 6단계: 테스트

**터미널 3: Hand target 전송**
```bash
source /opt/ros/humble/setup.bash
source /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/install/setup.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DOMAIN_ID=9
export ROS_LOCALHOST_ONLY=0

# Hand target 전송 (16개 관절, 모두 0 = 열린 상태)
ros2 topic pub --once /hand/target/right kistar_hand_ros2/msg/HandTarget \
  "{joint_targets: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], movement_duration: 1.0, hand_id: 0}"
```

---

## 📊 데이터 흐름

```
ROS2 /hand/target/right
    ↓
shm_ros2_bridge (handTargetCallback_R)
    ↓
SHM Hand_j_tar[Hand_R][16]
    ↓
ecatthread (1kHz 루프)
    ↓
EtherCAT JOINT_TARGET[16]
    ↓
🤖 KISTAR Hand 모터
```

---

## ✅ 확인 체크리스트

- [ ] EtherCAT 스레드 주석 해제 완료
- [ ] 빌드 완료
- [ ] R_Franka_KISTAR_Hand 실행 (EtherCAT 연결 확인)
- [ ] shm_ros2_bridge 실행
- [ ] `ros2 topic list`에서 `/hand/target/right` 확인
- [ ] Hand target 전송 테스트
- [ ] Hand 모터 움직임 확인

---

## 🔧 문제 해결

### EtherCAT 연결 실패
```bash
# 네트워크 인터페이스 확인
ip link show

# Hand_Arm_Setting.h에서 인터페이스 이름 확인
# ec_init("enp4s0") ← 이 부분이 실제 인터페이스와 맞는지 확인
```

### Hand가 움직이지 않음
1. `ros2 topic echo /hand/target/right`로 메시지 전송 확인
2. `monitor_shm.py`로 SHM의 `Hand_j_tar` 업데이트 확인
3. EtherCAT 상태 확인 (ecatthread 출력 확인)

---

*작성일: 2026-01-08*

