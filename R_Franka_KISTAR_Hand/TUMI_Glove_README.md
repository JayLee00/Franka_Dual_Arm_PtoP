# TUMI Glove Publisher

16자유도 **텍타일 엔코더 글러브** → 16자유도 **로봇 핸드** target 생성 노드.

- 글러브 펌웨어: 한 줄에 **16 joint** (MCP3208) + **21 tactile** (BMP384, Thumb 7 + Index 7 + Middle 7) 출력.
- 기존 1:1 매칭에 더해 **스케일**과 **촉각 기반 추가 각도** 모드를 지원합니다.

---

## 개발 순서 (권장)

1. **1단계: 1:1 매칭 유지 + 새 프로토콜 파싱**  
   - 글러브가 16+21 개 값을 한 줄로 보내므로, 37개 필드 파싱 및 16개만 사용하는 1:1 모드부터 동작 확인.

2. **2단계: 스케일 모드 (약 1.1)**  
   - `target = center + (encoder - center) * scale` 로 꽉 잡기.  
   - 각 구간별 limit(0~4096, -1000~1000 등) 유지.

3. **3단계: 촉각 gain 모드**  
   - `target = encoder + tactile * gain`  
   - Thumb/Index/Middle 각 7개 촉각 평균 → 해당 손가락의 PIP/DIP 관절에 gain 적용.

---

## 모드 설명

| 모드 | 설명 | 주요 파라미터 |
|------|------|----------------|
| **1** | 1:1 각도 매칭 (엔코더 값 그대로) | - |
| **2** | 스케일 적용 (더 꽉 잡기) | `scale` (기본 1.1) |
| **3** | 촉각으로 DIP/PIP 추가 각도 | `gain_pip`, `gain_dip` |
| **4** | 스케일 + 텍타일 gain (모드 2+3) | `scale`, `gain_pip`, `gain_dip` |

- **모드 3, 4** 관절 매핑: 각 손가락 7개 촉각 중 **최댓값** 사용
  - Thumb: joint 2, 3 ← 촉각 0~6
  - Index:  joint 5, 6 ← 촉각 7~13
  - Middle: joint 9, 10 ← 촉각 14~20

---

## 실행 방법

### 1. 환경 준비

- 글러브 펌웨어 업로드 후 USB 연결.
- 시리얼 한 줄 형식: `j0,j1,...,j15,p0.00,p1.00,...,p20.00` (37개 값).
- 시리얼 권한:
  ```bash
  sudo chmod 666 /dev/ttyUSB0
  # 또는 영구: sudo usermod -a -G dialout $USER 후 재로그인
  ```

### 2. 워크스페이스 소스

```bash
cd /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP
source install/setup.bash
```

(또는 `kistar_hand_ros2`가 설치된 워크스페이스에서 `source install/setup.bash` 실행.)

### 3. 노드 실행 (Python 직접 실행)

```bash
cd R_Franka_KISTAR_Hand
python3 TUMI_Glove_Publisher.py
```

- 기본: `port=/dev/ttyUSB0`, `baudrate=115200`, `mode=1`.

### 4. 모드/파라미터 변경

노드가 떠 있는 터미널에서 **다른 터미널**에서:

```bash
source install/setup.bash

# 모드 2 (스케일 1.1)
ros2 param set /tumi_glove_publisher_node mode 2
ros2 param set /tumi_glove_publisher_node scale 1.1

# 모드 3 (촉각 gain)
ros2 param set /tumi_glove_publisher_node mode 3
ros2 param set /tumi_glove_publisher_node gain_pip 0.02
ros2 param set /tumi_glove_publisher_node gain_dip 0.02

# 모드 4 (스케일 + 텍타일)
ros2 param set /tumi_glove_publisher_node mode 4
ros2 param set /tumi_glove_publisher_node scale 1.1
```

또는 **시작 시** 파라미터를 주려면 (같은 셸에서 한 번에):

```bash
cd R_Franka_KISTAR_Hand
python3 TUMI_Glove_Publisher.py --ros-args -p mode:=2 -p scale:=1.1
```

(필요 시 `-p port:=/dev/ttyUSB1` 등 추가.)

### 5. 포트/보드레이트

```bash
python3 TUMI_Glove_Publisher.py --ros-args -p port:=/dev/ttyUSB1 -p baudrate:=115200
```

### 6. 텍타일 히트맵 시각화

별도 터미널에서 실행 (target joint 발행 속도에 영향 없음):

```bash
source install/setup.bash
cd R_Franka_KISTAR_Hand
python3 tactile_heatmap_viz.py
```

- 구독 토픽: `/glove/tactile` (Float32MultiArray, 21개)
- Thumb/Index/Middle 각 7셀 히트맵, 색상: -100000 파랑, 0 초록, +100000 빨강
- `publish_tactile:=false` 로 퍼블리셔에서 촉각 발행 끄기 가능 (오버헤드 제거 시)

---

## 요약

- **글러브 펌웨어**: `Glove_firmware code.cpp` → 16 joint + 21 tactile 한 줄 출력.
- **기존 퍼블리셔**: `TATOS_Glove_Publisher.py` → 16개만 사용, 1:1.
- **새 퍼블리셔**: `TUMI_Glove_Publisher.py` → 37개 파싱, 모드 1(1:1) / 2(스케일) / 3(촉각 gain).
- **토픽**: `HandTarget` → `/hand/target/right` (기존과 동일).

실행 후 `shm_ros2_bridge` 등이 `/hand/target/right`를 구독하고 있으면 로봇 핸드로 target이 전달됩니다.
