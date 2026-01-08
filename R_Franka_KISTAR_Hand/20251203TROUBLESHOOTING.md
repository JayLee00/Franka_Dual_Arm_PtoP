# 문제 해결 가이드

## ❌ 문제: "No socket connection on enp4s0" / "Excecute as root"

### 원인
EtherCAT 통신을 위해서는 **root 권한**이 필요합니다. 일반 사용자로 실행하면 네트워크 인터페이스에 접근할 수 없습니다.

### 해결 방법

#### 방법 1: sudo로 실행 (권장)
```bash
cd build/test
sudo ./R_Franka_KISTAR_Hand
```

#### 방법 2: 네트워크 인터페이스 확인
```bash
# 네트워크 인터페이스 확인
ip addr show

# enp4s0가 있는지 확인
ip addr show enp4s0

# EtherCAT 인터페이스가 다운되어 있으면
sudo ip link set enp4s0 down
sudo ip link set enp4s0 up
```

#### 방법 3: 인터페이스 이름 확인
코드에서 `enp4s0`를 사용하고 있는데, 실제 인터페이스 이름이 다를 수 있습니다.

```bash
# 실제 인터페이스 이름 확인
ip addr show | grep -E "^[0-9]+:"

# 또는
ls /sys/class/net/
```

인터페이스 이름이 다르면 `Hand_Arm_Setting.h`의 `ethercat_run()` 함수에서 수정:
```cpp
if (ec_init("enp4s0"))  // ← 여기를 실제 인터페이스 이름으로 변경
```

### 실행 순서

1. **터미널 1: 로봇 제어 프로그램 (sudo 필요)**
   ```bash
   cd /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/build/test
   sudo ./R_Franka_KISTAR_Hand
   ```

2. **터미널 2: ROS2 브리지 (일반 사용자)**
   ```bash
   cd /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ros2 run kistar_hand_ros2 shm_ros2_bridge
   ```

### 추가 확인 사항

#### 1. 네트워크 인터페이스 확인
```bash
# 모든 네트워크 인터페이스 확인
ip addr show

# EtherCAT용 인터페이스 확인 (보통 enp4s0, eth0 등)
```

#### 2. EtherCAT 인터페이스 설정
```bash
# 인터페이스가 UP 상태인지 확인
ip link show enp4s0

# DOWN 상태면 UP으로 설정
sudo ip link set enp4s0 up

# IP 주소 제거 (EtherCAT은 IP가 필요 없음)
sudo ip addr flush dev enp4s0
```

#### 3. 권한 문제
```bash
# 현재 사용자가 sudo 권한이 있는지 확인
sudo -v

# sudo 없이 실행하려면 (권장하지 않음)
# setcap으로 실행 파일에 권한 부여 (복잡함)
```

### 예상 출력 (정상 작동 시)

```
Arm and Hand System Test 
Shared Memory Connection Success
🔗 Connecting to Franka...
✅ Connected to Franka at 172.16.0.2
🚀 Moving to safe position...
✅ Reached safe position!
ec_init on enp4s0 succeeded.
1 slaves found and configured.
Operational state reached for all slaves.
Operation Start
```

### 문제가 계속되면

1. **인터페이스 이름 확인 및 수정**
   ```bash
   # 실제 인터페이스 이름 확인
   ip addr show
   
   # Hand_Arm_Setting.h에서 수정
   # Line 516: ec_init("enp4s0") → 실제 인터페이스 이름으로 변경
   ```

2. **네트워크 인터페이스 재설정**
   ```bash
   sudo ip link set enp4s0 down
   sudo ip link set enp4s0 up
   sudo ip addr flush dev enp4s0
   ```

3. **EtherCAT 드라이버 확인**
   ```bash
   # EtherCAT 관련 커널 모듈 확인
   lsmod | grep ec
   
   # 또는
   dmesg | grep -i ethercat
   ```

