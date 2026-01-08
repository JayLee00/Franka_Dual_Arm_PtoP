# ROS2 패키지 구조 상세 설명

## 📦 1. 패키지 이름: `kistar_hand_ros2`

### `package.xml` 파일

```xml
<package format="3">
  <name>kistar_hand_ros2</name>  <!-- 👈 여기서 패키지 이름 정의 -->
  <version>0.1.0</version>
  ...
  <export>
    <build_type>ament_cmake</build_type>  <!-- CMake 빌드 시스템 사용 -->
  </export>
</package>
```

**역할:**
- ROS2 패키지의 **메타데이터** 정의
- 패키지 이름, 버전, 의존성 정보 저장
- `ros2 pkg list` 명령어로 이 이름이 표시됨

**위치:**
```
R_Franka_KISTAR_Hand/
└── package.xml  ← 패키지 루트에 있어야 함
```

---

## 🔨 2. 실행 파일 이름: `shm_ros2_bridge`

### `CMakeLists.txt` 파일

```cmake
# 1단계: 실행 파일 생성
add_executable(shm_ros2_bridge src/shm_ros2_bridge.cpp)
#              ^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^^^^^^
#              실행파일 이름    소스 파일 경로

# 2단계: 의존성 연결
ament_target_dependencies(shm_ros2_bridge
    rclcpp        # ROS2 C++ 라이브러리
    std_msgs      # 표준 메시지 타입
    builtin_interfaces
)

# 3단계: 라이브러리 링크
target_link_libraries(shm_ros2_bridge
    soem          # EtherCAT 라이브러리
    franka        # Franka 로봇 라이브러리
)

# 4단계: 설치 경로 지정
install(TARGETS shm_ros2_bridge
    DESTINATION lib/${PROJECT_NAME}
    #           ^^^ ^^^^^^^^^^^^^^
    #           lib/ kistar_hand_ros2/
)
```

**빌드 과정:**

1. **소스 파일 컴파일**
   ```
   src/shm_ros2_bridge.cpp → (컴파일) → shm_ros2_bridge (실행 파일)
   ```

2. **실행 파일 생성 위치**
   ```
   build/kistar_hand_ros2/shm_ros2_bridge  (빌드 중)
   ```

3. **설치 위치**
   ```
   install/kistar_hand_ros2/lib/kistar_hand_ros2/shm_ros2_bridge
   #       ^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^
   #       패키지명            lib/패키지명/       실행파일명
   ```

---

## 🚀 3. `ros2 run` 명령어 동작 원리

### 명령어
```bash
ros2 run kistar_hand_ros2 shm_ros2_bridge
```

### 실행 과정

#### 1단계: 패키지 찾기
```bash
# ROS2가 다음 경로에서 패키지 검색
$AMENT_PREFIX_PATH/install/kistar_hand_ros2/
# 또는
/opt/ros/humble/share/kistar_hand_ros2/
```

**확인 방법:**
```bash
ros2 pkg list | grep kistar
# 출력: kistar_hand_ros2
```

#### 2단계: 실행 파일 찾기
```bash
# 패키지 내부에서 실행 파일 검색
install/kistar_hand_ros2/lib/kistar_hand_ros2/shm_ros2_bridge
#       ^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^
#       패키지명            lib/패키지명/       실행파일명
```

**실제 경로 확인:**
```bash
# 빌드 후 실제 경로
/home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/install/kistar_hand_ros2/lib/kistar_hand_ros2/shm_ros2_bridge
```

#### 3단계: 실행
```bash
# ROS2가 찾은 실행 파일을 실행
./install/kistar_hand_ros2/lib/kistar_hand_ros2/shm_ros2_bridge
```

---

## 📁 4. 전체 디렉토리 구조

```
R_Franka_KISTAR_Hand/
├── package.xml                    # 패키지 메타데이터 (패키지 이름 정의)
├── CMakeLists.txt                 # 빌드 설정 (실행 파일 등록)
│
├── src/
│   └── shm_ros2_bridge.cpp        # 소스 파일
│
├── build/                         # 빌드 중간 파일
│   └── kistar_hand_ros2/
│       └── shm_ros2_bridge        # 컴파일된 실행 파일 (임시)
│
└── install/                       # 설치된 파일 (최종)
    └── kistar_hand_ros2/
        ├── lib/
        │   └── kistar_hand_ros2/
        │       └── shm_ros2_bridge  # 👈 ros2 run이 찾는 파일
        │
        ├── share/
        │   └── kistar_hand_ros2/
        │       ├── package.xml      # 설치된 패키지 정보
        │       └── msg/             # 메시지 파일들
        │
        └── include/
            └── kistar_hand_ros2/    # 헤더 파일들
```

---

## 🔍 5. 각 단계별 상세 설명

### Step 1: `package.xml`에서 패키지 이름 정의

```xml
<name>kistar_hand_ros2</name>
```

**역할:**
- ROS2 시스템이 이 패키지를 식별하는 **고유 이름**
- `ros2 pkg list`, `ros2 run` 등에서 사용
- **중요**: 이 이름은 고유해야 함 (다른 패키지와 겹치면 안 됨)

### Step 2: `CMakeLists.txt`에서 실행 파일 등록

```cmake
add_executable(shm_ros2_bridge src/shm_ros2_bridge.cpp)
```

**의미:**
- `shm_ros2_bridge`: 생성될 실행 파일의 이름
- `src/shm_ros2_bridge.cpp`: 컴파일할 소스 파일
- 빌드 시 `build/` 디렉토리에 실행 파일 생성

### Step 3: 설치 경로 지정

```cmake
install(TARGETS shm_ros2_bridge
    DESTINATION lib/${PROJECT_NAME}
)
```

**의미:**
- `${PROJECT_NAME}` = `kistar_hand_ros2` (CMakeLists.txt에서 정의)
- 최종 경로: `install/kistar_hand_ros2/lib/kistar_hand_ros2/shm_ros2_bridge`
- `ros2 run`이 이 경로에서 실행 파일을 찾음

### Step 4: 빌드 및 설치

```bash
cd build
cmake ..
make
# 또는
colcon build
```

**결과:**
- `build/`에 임시 실행 파일 생성
- `install/`에 최종 실행 파일 설치
- `ros2 run`은 `install/` 경로를 사용

---

## 🎯 6. `ros2 run` 명령어 해부

```bash
ros2 run kistar_hand_ros2 shm_ros2_bridge
#       ^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^
#       패키지 이름        실행 파일 이름
```

### 내부 동작

1. **패키지 검색**
   ```bash
   # ROS2가 다음 경로에서 패키지 검색
   $AMENT_PREFIX_PATH/share/kistar_hand_ros2/
   ```

2. **실행 파일 검색**
   ```bash
   # 패키지 내부에서 실행 파일 검색
   $AMENT_PREFIX_PATH/lib/kistar_hand_ros2/shm_ros2_bridge
   ```

3. **환경 변수 확인**
   ```bash
   echo $AMENT_PREFIX_PATH
   # 출력: /home/prime/.../install
   ```

4. **실행**
   ```bash
   $AMENT_PREFIX_PATH/lib/kistar_hand_ros2/shm_ros2_bridge
   ```

---

## 📌 7. 핵심 포인트 정리

### 패키지 이름 (`kistar_hand_ros2`)
- ✅ `package.xml`의 `<name>` 태그에 정의
- ✅ ROS2 시스템이 패키지를 식별하는 고유 이름
- ✅ `ros2 pkg list`로 확인 가능

### 실행 파일 이름 (`shm_ros2_bridge`)
- ✅ `CMakeLists.txt`의 `add_executable()`에 정의
- ✅ C++ 소스 파일을 컴파일하여 생성
- ✅ 빌드 후 `install/lib/패키지명/실행파일명`에 설치

### 실행 경로
```
install/kistar_hand_ros2/lib/kistar_hand_ros2/shm_ros2_bridge
#       ^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^
#       패키지명            lib/패키지명/       실행파일명
```

---

## 🔧 8. 실제 확인 방법

### 패키지 확인
```bash
ros2 pkg list | grep kistar
# 출력: kistar_hand_ros2
```

### 실행 파일 경로 확인
```bash
find install -name "shm_ros2_bridge" -type f
# 출력: install/kistar_hand_ros2/lib/kistar_hand_ros2/shm_ros2_bridge
```

### 직접 실행 (ros2 run 없이)
```bash
./install/kistar_hand_ros2/lib/kistar_hand_ros2/shm_ros2_bridge
```

### ros2 run으로 실행
```bash
ros2 run kistar_hand_ros2 shm_ros2_bridge
# 위의 직접 실행과 동일한 결과
```

---

*작성일: 2026-01-08*

