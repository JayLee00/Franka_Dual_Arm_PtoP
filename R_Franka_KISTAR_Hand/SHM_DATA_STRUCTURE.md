# Shared Memory (SHM) 데이터 구조 설명

## 개요
`SHMmsgs` 구조체는 KISTAR Hand와 Franka 로봇 팔 간의 데이터를 공유하기 위한 공유 메모리 구조입니다.

---

## R_gravity / L_gravity 설명

### 정의
```cpp
std::array<double, 7> R_gravity;  // 오른쪽 팔 중력 보상 토크
std::array<double, 7> L_gravity;  // 왼쪽 팔 중력 보상 토크
```

### 의미
- **중력 보상 토크 (Gravity Compensation Torque)**: 각 관절에서 중력을 상쇄하기 위해 필요한 토크 값
- **단위**: `[Nm]` (뉴턴 미터)
- **크기**: 7개 요소 (Franka 로봇은 7 DOF)

### 계산 방법
Franka의 `Model::gravity()` 함수를 사용하여 계산:
```cpp
franka::Model model = robot.loadModel();
std::array<double, 7> gravity = model.gravity(robot_state);
// 또는
std::array<double, 7> gravity = model.gravity(robot_state.q, robot_state.m_total, 
                                               robot_state.F_x_Ctotal, 
                                               {0.0, 0.0, -9.81});
```

### 용도
- **토크 제어 시**: 중력 보상을 위해 사용
- **외력 추정**: 실제 측정 토크에서 중력 토크를 빼면 외력만 추출 가능
- **제어 안정성**: 중력 보상을 통해 로봇이 특정 자세를 유지할 수 있음

### 예시
```cpp
// 외력 추정 예시
tau_ext = tau_measured - gravity - initial_tau_ext;
```

---

## SHM 데이터 구조 전체 정리

### 1. Hand (KISTAR Hand) 관련 데이터

#### Hand 제어 명령 (PC → Hand)
```cpp
int16_t Hand_j_pos[Hand_Num][Hand_DOF];        // Hand 목표 위치 [2][16]
int16_t Hand_j_tar[Hand_Num][Hand_DOF];        // Hand 타겟 위치 [2][16]
bool Hand_CMD_Status[Hand_Num];                // Hand 명령 상태 [2]
double hand_movement_duration[Hand_Num];       // Hand 이동 시간 [2]
uint8_t Hand_mode[Hand_Num];                   // Hand 모드 [2]
uint8_t Hand_servo_on[Hand_Num];               // Hand 서보 ON/OFF [2]
```

#### Hand 현재 상태 (Hand → PC)
```cpp
int16_t Hand_j_cur[Hand_Num][Hand_DOF];        // Hand 현재 위치 [2][16]
int16_t Hand_j_kin[Hand_Num][Kinesthetic_Sensor_DATA_NUM];  // Kinesthetic 센서 [2][12]
int16_t Hand_j_tac[Hand_Num][Tactile_Sensor_DATA_NUM];    // Tactile 센서 [2][60]
```

#### Hand 별도 배열 (오른쪽/왼쪽)
```cpp
std::array<int, 16> R_Hand_j_pos;              // 오른쪽 Hand 목표 위치
std::array<int, 16> R_Hand_j_cur;              // 오른쪽 Hand 현재 위치
std::array<int, 16> L_Hand_j_pos;              // 왼쪽 Hand 목표 위치
std::array<int, 16> L_Hand_j_cur;              // 왼쪽 Hand 현재 위치
```

**센서 데이터 크기:**
- `Kinesthetic_Sensor_DATA_NUM = 4*3 = 12` (4개 센서 × 3축)
- `Tactile_Sensor_DATA_NUM = 4*15 = 60` (4개 센서 × 15개 셀)

---

### 2. Arm (Franka) 관련 데이터

#### Arm 기본 상태
```cpp
double Arm_j_pos[Arm_Num][Arm_DOF];            // 관절 위치 [2][7] [rad]
double Arm_j_tar[Arm_Num][Arm_DOF];            // 관절 목표 위치 [2][7] [rad]
double Arm_j_vel[Arm_Num][Arm_DOF];            // 관절 속도 [2][7] [rad/s]
double Arm_j_tq[Arm_Num][Arm_DOF];             // 관절 토크 [2][7] [Nm]
double Arm_C_Pos[Arm_Num][16];                 // 카테시안 공간 포즈 (End-effector) [2][16]
```

#### Arm 상세 상태 (오른쪽)
```cpp
franka::RobotState R_robot_state;              // 오른쪽 로봇 전체 상태
std::array<double, 7> R_q;                     // 오른쪽 관절 위치 [rad]
std::array<double, 7> R_qdes;                  // 오른쪽 관절 목표 위치 [rad]
std::array<double, 7> R_tau_d_last;            // 오른쪽 마지막 토크 명령 [Nm]
std::array<double, 7> R_gravity;               // 오른쪽 중력 보상 토크 [Nm]
```

#### Arm 상세 상태 (왼쪽)
```cpp
franka::RobotState L_robot_state;              // 왼쪽 로봇 전체 상태
std::array<double, 7> L_q;                      // 왼쪽 관절 위치 [rad]
std::array<double, 7> L_qdes;                   // 왼쪽 관절 목표 위치 [rad]
std::array<double, 7> L_tau_d_last;             // 왼쪽 마지막 토크 명령 [Nm]
std::array<double, 7> L_gravity;                // 왼쪽 중력 보상 토크 [Nm]
```

**Franka::RobotState 포함 정보:**
- `O_T_EE`: End effector pose in base frame (4x4 행렬)
- `q`, `dq`: 관절 위치, 속도
- `tau_J`: 측정된 관절 토크
- `O_F_ext_hat_K`: 외력 추정
- `robot_mode`: 로봇 모드 (Idle, Move, etc.)
- 기타 상세 상태 정보

---

### 3. Gripper 관련 데이터

```cpp
bool franka_L_gripper_ishoming;                // 왼쪽 그리퍼 홈 위치 여부
bool franka_L_gripper_isgrasping;              // 왼쪽 그리퍼 그랩 상태
uint8_t franka_L_gripper_Mode;                 // 왼쪽 그리퍼 모드
double franka_L_gripper_grasping_width;        // 그랩 폭 [m]
double franka_L_gripper_grasping_speed;        // 그랩 속도 [m/s]
double franka_L_gripper_grasping_force;        // 그랩 힘 [N]
double franka_L_gripper_current_width;        // 현재 폭 [m]
```

**참고**: 현재는 왼쪽 그리퍼만 구현되어 있음

---

### 4. 시스템 제어 데이터

```cpp
uint16_t Motion_Sequence;                      // 모션 시퀀스 번호
std::atomic<int> process_num;                   // 공유 메모리를 사용하는 프로세스 수
```

---

## 데이터 흐름

### Hand 데이터 흐름
```
EtherCAT 통신
    ↓
Hand 센서 데이터 읽기 (Hand_j_cur, Hand_j_kin, Hand_j_tac)
    ↓
SHM에 쓰기
    ↓
ROS2 Bridge가 읽어서 ROS2 토픽으로 발행

ROS2 토픽에서 Hand 목표 수신
    ↓
SHM에 쓰기 (Hand_j_tar, Hand_j_pos)
    ↓
EtherCAT 통신으로 Hand에 전송
```

### Franka Arm 데이터 흐름
```
Franka 로봇
    ↓
robot.readOnce() 또는 robot.control() 콜백
    ↓
SHM에 쓰기 (Arm_j_pos, Arm_j_vel, Arm_j_tq, R_robot_state, R_q, R_gravity 등)
    ↓
ROS2 Bridge가 읽어서 ROS2 토픽으로 발행

ROS2 토픽에서 Arm 목표 수신
    ↓
SHM에 쓰기 (Arm_j_tar, R_qdes)
    ↓
Franka 제어 루프에서 읽어서 robot.control()에 사용
```

---

## 상수 정의

```cpp
#define Hand_Num 2          // Hand 개수 (오른쪽, 왼쪽)
#define Hand_DOF 16         // Hand 자유도
#define Arm_Num 2           // Arm 개수 (오른쪽, 왼쪽)
#define Arm_DOF 7           // Arm 자유도 (Franka는 7 DOF)

#define Hand_R   0          // 오른쪽 Hand 인덱스
#define Hand_L   1          // 왼쪽 Hand 인덱스
#define Arm_R    0          // 오른쪽 Arm 인덱스
#define Arm_L    1          // 왼쪽 Arm 인덱스

#define Kinesthetic_Sensor_DATA_NUM 4*3   // 12 (4개 센서 × 3축)
#define Tactile_Sensor_DATA_NUM 4*15      // 60 (4개 센서 × 15개 셀)
```

---

## 공유 메모리 키

```cpp
static const key_t shm_msg_key = 0x3940;  // 메인 SHM 키
static const key_t shm_rd_key = 10334;     // 읽기 전용 SHM 키 (미사용?)
```

---

## 사용 예시

### SHM 초기화
```cpp
SHMmsgs *shm_msgs_;
int shm_id;
init_shm(shm_msg_key, shm_id, &shm_msgs_);
```

### 데이터 읽기
```cpp
// 관절 위치 읽기
double joint_pos[7];
for (int i = 0; i < 7; i++) {
    joint_pos[i] = shm_msgs_->Arm_j_pos[Arm_R][i];
}

// 중력 토크 읽기
std::array<double, 7> gravity = shm_msgs_->R_gravity;
```

### 데이터 쓰기
```cpp
// 관절 목표 설정
for (int i = 0; i < 7; i++) {
    shm_msgs_->Arm_j_tar[Arm_R][i] = target_joint[i];
}
```

---

## 주의사항

1. **동시 접근**: 여러 프로세스가 동시에 SHM에 접근할 수 있으므로 동기화 필요
2. **데이터 타입**: Hand는 `int16_t`, Arm은 `double` 사용
3. **프로세스 관리**: `process_num`을 통해 공유 메모리 생명주기 관리
4. **메모리 정리**: 프로그램 종료 시 `deleteSharedMemory()` 호출 필요

---

## 날짜
2024년 12월 3일

