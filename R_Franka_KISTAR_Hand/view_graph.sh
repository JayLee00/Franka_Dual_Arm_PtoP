#!/bin/bash

# ROS2 그래프 시각화 스크립트

echo "📊 ROS2 그래프 시각화 도구"
echo ""

# ROS2 환경 활성화
source /opt/ros/humble/setup.bash 2>/dev/null
if [ -f install/setup.bash ]; then
    source install/setup.bash
fi

echo "1️⃣  노드 목록:"
ros2 node list
echo ""

echo "2️⃣  토픽 목록:"
ros2 topic list
echo ""

echo "3️⃣  브리지 노드 정보:"
if ros2 node list | grep -q shm_ros2_bridge; then
    ros2 node info /shm_ros2_bridge
else
    echo "   ⚠️  shm_ros2_bridge 노드가 실행되지 않았습니다."
    echo "   다음 명령어로 노드를 실행하세요:"
    echo "   ros2 run kistar_hand_ros2 shm_ros2_bridge"
fi
echo ""

echo "4️⃣  그래프 시각화 옵션:"
echo "   - GUI 그래프: rqt_graph (설치 필요: sudo apt install ros-humble-rqt-graph)"
echo "   - 텍스트 기반: 위의 노드/토픽 정보 참조"
echo ""

# rqt_graph 사용 가능 여부 확인
if command -v rqt_graph &> /dev/null; then
    echo "✅ rqt_graph 사용 가능"
    echo "   실행하려면: rqt_graph"
elif python3 -c "import rqt_graph" 2>/dev/null; then
    echo "✅ rqt_graph 모듈 사용 가능"
    echo "   실행하려면: ros2 run rqt_graph rqt_graph"
else
    echo "⚠️  rqt_graph가 설치되지 않았습니다."
    echo "   설치: sudo apt install ros-humble-rqt-graph"
fi

