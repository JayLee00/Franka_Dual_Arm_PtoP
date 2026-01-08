#!/bin/bash

# ROS2 Humble 설치 스크립트 (Ubuntu 22.04)

set -e

echo "🚀 ROS2 Humble 설치를 시작합니다..."

# 0. GPG 키 문제 해결 (Kitware 저장소)
echo "🔑 GPG 키 문제를 해결합니다..."
if [ -f /etc/apt/sources.list.d/kitware.list ] || grep -q "apt.kitware.com" /etc/apt/sources.list.d/*.list 2>/dev/null; then
    echo "   Kitware GPG 키를 추가합니다..."
    # 최신 방법: 키링 파일 사용
    if [ ! -f /usr/share/keyrings/kitware-archive-keyring.gpg ]; then
        curl -fsSL https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | \
        sudo gpg --dearmor -o /usr/share/keyrings/kitware-archive-keyring.gpg 2>/dev/null || \
        echo "   ⚠️  GPG 키 추가 실패 (계속 진행합니다)"
    fi
    # 또는 기존 방법
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 16FAAD7AF99A65E2 2>/dev/null || \
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 16FAAD7AF99A65E2 2>/dev/null || \
    echo "   ⚠️  GPG 키 추가 실패 (계속 진행합니다)"
fi

# 1. Locale 설정 확인
if ! locale | grep -q UTF-8; then
    echo "⚠️  UTF-8 locale 설정이 필요합니다."
    sudo locale-gen en_US en_US.UTF-8
    sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
    export LANG=en_US.UTF-8
fi

# 2. 필수 패키지 설치
echo "📦 필수 패키지를 설치합니다..."
# GPG 오류가 있어도 계속 진행
sudo apt update || echo "⚠️  일부 저장소 오류가 있지만 계속 진행합니다..."
sudo apt install -y \
    software-properties-common \
    curl \
    gnupg \
    lsb-release

# 3. ROS2 저장소 추가
echo "📚 ROS2 저장소를 추가합니다..."
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2-latest.list > /dev/null

# 4. 패키지 목록 업데이트
echo "🔄 패키지 목록을 업데이트합니다..."
# GPG 오류가 있어도 계속 진행
sudo apt update || echo "⚠️  일부 저장소 오류가 있지만 계속 진행합니다..."

# 5. ROS2 Humble Desktop 설치
echo "📥 ROS2 Humble Desktop을 설치합니다 (시간이 걸릴 수 있습니다)..."
sudo apt install -y ros-humble-desktop

# 6. 개발 도구 설치
echo "🛠️  개발 도구를 설치합니다..."
sudo apt install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    build-essential

# 7. rosdep 초기화
echo "🔧 rosdep을 초기화합니다..."
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    sudo rosdep init
fi
rosdep update

# 8. 환경 설정
echo "✅ ROS2 설치가 완료되었습니다!"
echo ""
echo "📝 다음 명령어로 ROS2 환경을 설정하세요:"
echo "   source /opt/ros/humble/setup.bash"
echo ""
echo "또는 ~/.bashrc에 다음을 추가하세요:"
echo "   echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc"

