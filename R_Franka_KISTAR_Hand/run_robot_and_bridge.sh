#!/bin/bash

# 로봇 제어 프로그램과 ROS2 브리지를 실행하는 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 KISTAR Hand & Franka Arm 시스템 시작"
echo ""

# ROS2 환경 활성화
source /opt/ros/humble/setup.bash 2>/dev/null
if [ -f install/setup.bash ]; then
    source install/setup.bash
fi

# 1. 로봇 제어 프로그램 실행 (백그라운드)
echo "1️⃣  로봇 제어 프로그램 실행 중..."
if [ -f "build/test/R_Franka_KISTAR_Hand" ]; then
    cd build/test
    sudo ./R_Franka_KISTAR_Hand &
    ROBOT_PID=$!
    echo "   ✅ 로봇 제어 프로그램 시작됨 (PID: $ROBOT_PID)"
    cd "$SCRIPT_DIR"
    sleep 2  # shm 생성 대기
else
    echo "   ❌ R_Franka_KISTAR_Hand 실행 파일을 찾을 수 없습니다."
    echo "   빌드: cd build && cmake .. && make -j\$(nproc)"
    exit 1
fi

# 2. ROS2 브리지 실행
echo "2️⃣  ROS2 브리지 노드 실행 중..."
if command -v ros2 &> /dev/null; then
    ros2 run kistar_hand_ros2 shm_ros2_bridge &
    BRIDGE_PID=$!
    echo "   ✅ ROS2 브리지 시작됨 (PID: $BRIDGE_PID)"
else
    echo "   ❌ ROS2가 설치되지 않았습니다."
    kill $ROBOT_PID 2>/dev/null
    exit 1
fi

echo ""
echo "✅ 시스템이 실행 중입니다!"
echo ""
echo "📊 확인 명령어:"
echo "   - 토픽 목록: ros2 topic list"
echo "   - 데이터 확인: ros2 topic echo /franka/arm_state/right"
echo "   - 그래프: rqt_graph"
echo ""
echo "🛑 종료하려면:"
echo "   sudo kill $ROBOT_PID $BRIDGE_PID"
echo ""
echo "또는 Ctrl+C를 누르면 자동으로 종료됩니다."

# 신호 처리
trap "echo ''; echo '🛑 시스템 종료 중...'; sudo kill $ROBOT_PID $BRIDGE_PID 2>/dev/null; wait; exit" INT TERM

# 대기
wait

