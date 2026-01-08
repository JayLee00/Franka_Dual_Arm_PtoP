# libfranka 0.18.1 빌드 트러블슈팅 가이드

## 문제 상황
- **원래 오류**: `libfranka: Incompatible library version (server version: 10, library version: 8)`
- **해결 방법**: libfranka를 버전 0.18.1로 업데이트 및 재빌드

## 해결한 문제들

### 1. 버전 호환성 문제
**문제**: 로봇 서버 버전(10)과 라이브러리 버전(8) 불일치

**해결**:
- `libfranka`를 버전 0.18.1로 체크아웃
- `CMakeLists.txt`에서 버전을 `0.15.3` → `0.18.1`로 수정

```cmake
# libfranka/CMakeLists.txt
set(libfranka_VERSION 0.18.1)  # 0.15.3에서 변경
```

---

### 2. CMake 최소 버전 오류
**오류 메시지**:
```
CMake Error at common/CMakeLists.txt:1 (cmake_minimum_required):
Compatibility with CMake < 3.5 has been removed from CMake.
```

**해결**:
```cmake
# libfranka/common/CMakeLists.txt
cmake_minimum_required(VERSION 3.6)  # 3.0.2에서 변경
```

---

### 3. std::optional 헤더 누락
**오류 메시지**:
```
error: 'optional' in namespace 'std' does not name a template type
```

**해결**:
```cpp
// libfranka/include/franka/robot.h
#include <optional>  // 추가
```

---

### 4. accelerometer 필드 문제
**오류 메시지**:
```
error: 'const struct research_interface::robot::RobotState' has no member named 'accelerometer_top'
```

**해결**:
```cpp
// libfranka/src/robot_impl.cpp
// 다음 두 줄을 주석 처리
// converted.accelerometer_top = robot_state.accelerometer_top;
// converted.accelerometer_bottom = robot_state.accelerometer_bottom;
```

**이유**: 0.18.1 버전의 `research_interface::robot::RobotState`에는 이 필드가 없음

---

### 5. TinyXML2 링킹 문제
**오류 메시지**:
```
CMake Error: By not providing "Findtinyxml2.cmake" in CMAKE_MODULE_PATH
```

**해결**:
```cmake
# libfranka/CMakeLists.txt

# Dependencies 섹션에 추가
find_package(TinyXML2 REQUIRED)  # 추가

# target_link_libraries에 추가
target_link_libraries(franka PRIVATE
  Poco::Foundation
  Poco::Net
  Eigen3::Eigen3
  Threads::Threads
  pinocchio::pinocchio
  TinyXML2::TinyXML2  # 추가
)
```

**참고**: `libfranka/cmake/FindTinyXML2.cmake` 파일이 이미 존재하므로 `find_package(TinyXML2 REQUIRED)`만 호출하면 됨

---

### 6. 존재하지 않는 소스 파일 참조
**오류 메시지**:
```
CMake Error: Cannot find source file: libfranka/src/library_downloader.cpp
```

**해결**: `CMakeLists.txt`에서 존재하지 않는 파일 제거
```cmake
# libfranka/CMakeLists.txt - add_library 섹션에서 제거
# src/library_downloader.cpp  # 제거
# src/library_loader.cpp      # 제거
# src/model_library.cpp       # 제거
```

---

### 7. 누락된 소스 파일 추가
**문제**: `joint_velocity_limits.cpp`와 `async_position_control_handler.cpp`가 빌드에 포함되지 않음

**해결**:
```cmake
# libfranka/CMakeLists.txt - add_library 섹션에 추가
add_library(franka SHARED
  # ... 기존 파일들 ...
  src/robot_model.cpp
  src/joint_velocity_limits.cpp                    # 추가
  src/async_control/async_position_control_handler.cpp  # 추가
  
  src/logging/cout_logging_sink.cpp
  # ...
)
```

---

## 최종 빌드 명령어

```bash
cd /home/prime/KISTAR_Hand_RTOS-master/Franka_Dual_Arm_PtoP/R_Franka_KISTAR_Hand/libfranka

# 빌드 디렉토리 정리 (sudo 필요)
sudo rm -rf build
mkdir build && cd build

# CMake 설정
sudo cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_PREFIX_PATH=/opt/openrobots/lib/cmake \
      -DBUILD_TESTS=OFF \
      -DBUILD_EXAMPLES=OFF \
      ..

# 빌드
sudo make -j$(nproc)

# 설치
sudo make install
```

---

## 수정된 파일 목록

1. `libfranka/CMakeLists.txt`
   - 버전: `0.15.3` → `0.18.1`
   - `find_package(TinyXML2 REQUIRED)` 추가
   - `target_link_libraries`에 `TinyXML2::TinyXML2` 추가
   - 존재하지 않는 소스 파일 제거
   - 누락된 소스 파일 추가

2. `libfranka/common/CMakeLists.txt`
   - `cmake_minimum_required(VERSION 3.6)`로 변경

3. `libfranka/include/franka/robot.h`
   - `#include <optional>` 추가

4. `libfranka/src/robot_impl.cpp`
   - `accelerometer_top`, `accelerometer_bottom` 할당 주석 처리

---

## 확인 사항

빌드 성공 후 확인:
```bash
# 라이브러리 버전 확인
ls -lh /usr/local/lib/libfranka.so*

# 심볼 확인 (필요한 함수들이 포함되어 있는지)
nm -D /usr/local/lib/libfranka.so.0.18.1 | grep -E "JointVelocityLimitsConfig|AsyncPositionControlHandler"
```

---

## 참고 사항

- **경고 메시지**: `#pragma message: Please update your includes from 'hpp/fcl' to 'coal'`는 무시해도 됨 (pinocchio 라이브러리의 deprecation 알림)
- **권한 문제**: 빌드 디렉토리가 root 소유일 경우 `sudo` 사용 필요
- **Git 작업**: 버전 체크아웃 전에 로컬 변경사항 `git stash` 필요

---

## 날짜
2024년 12월 3일

