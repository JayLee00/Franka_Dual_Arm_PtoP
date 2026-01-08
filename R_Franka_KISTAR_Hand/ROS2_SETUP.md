# ROS2 설치 위치 및 실행 방법

## 📍 ROS2 설치 위치

ROS2 Humble이 다음 위치에 설치되어 있습니다:
```
/opt/ros/humble/
```

주요 디렉토리:
- `/opt/ros/humble/bin/` - 실행 파일
- `/opt/ros/humble/lib/` - 라이브러리
- `/opt/ros/humble/share/` - 패키지 및 리소스
- `/opt/ros/humble/setup.bash` - 환경 설정 스크립트

## 🚀 ROS2 실행 방법

### 방법 1: 현재 터미널에서 임시로 활성화
```bash
source /opt/ros/humble/setup.bash
```

### 방법 2: 영구적으로 활성화 (권장)
`~/.bashrc` 파일에 다음 줄을 추가:
```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 방법 3: 스크립트로 확인
```bash
# ROS2 환경 활성화
source /opt/ros/humble/setup.bash

# 설치 확인
ros2 --help
```

## ✅ 설치 확인 명령어

```bash
# ROS2 환경 활성화 후
source /opt/ros/humble/setup.bash

# 배포판 확인 (ROS2 Humble은 --version 옵션이 없음)
echo $ROS_DISTRO
# 출력: humble

# 시스템 상태 확인 (권장)
ros2 doctor --report

# 도움말 확인
ros2 --help

# 설치된 패키지 확인
ros2 pkg list

# 노드 실행 예제
ros2 run demo_nodes_cpp talker
```

## 🔧 워크스페이스 설정

ROS2 워크스페이스를 만들고 빌드하려면:

```bash
# 1. 워크스페이스 디렉토리 생성
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

# 2. ROS2 환경 활성화
source /opt/ros/humble/setup.bash

# 3. 패키지 빌드
colcon build

# 4. 워크스페이스 환경 활성화
source install/setup.bash
```

## 📝 현재 프로젝트 빌드 방법

```bash
# 1. ROS2 환경 활성화
source /opt/ros/humble/setup.bash

# 2. 프로젝트 디렉토리로 이동
cd /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand

# 3. 빌드 (ROS2 워크스페이스로 사용)
colcon build

# 4. 환경 활성화
source install/setup.bash

# 5. 노드 실행
ros2 run kistar_hand_ros2 shm_ros2_bridge
```

