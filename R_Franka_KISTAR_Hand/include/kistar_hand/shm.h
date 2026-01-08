
#include <atomic>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <time.h>
#include <unistd.h>
#include <iostream>
#include <mutex>
#include <franka/model.h>

#if defined(__x86_64) || defined(__i386)
#define cpu_relax() __asm__("pause" :: \
                                : "memory")
#else
#define cpu_relax() __asm__("" :: \
                                : "memory")
#endif

#define Hand_Num 2
#define Hand_DOF 16
#define Kinesthetic_Sensor_DATA_NUM 4*3
#define Tactile_Sensor_DATA_NUM 4*15

#define Arm_Num 2
#define Arm_DOF 7

#define Hand_R   0
#define Hand_L   1

#define Arm_R   0
#define Arm_L   1

typedef struct SHMmsgs
{
    uint16_t Motion_Sequence; 
    int16_t Hand_j_pos[Hand_Num][Hand_DOF];
    int16_t Hand_j_tar[Hand_Num][Hand_DOF];
    bool Hand_CMD_Status[Hand_Num];
    double hand_movement_duration[Hand_Num];

    int16_t Hand_j_cur[Hand_Num][Hand_DOF];
    int16_t Hand_j_kin[Hand_Num][Kinesthetic_Sensor_DATA_NUM];
    int16_t Hand_j_tac[Hand_Num][Tactile_Sensor_DATA_NUM];

    uint8_t Hand_mode[Hand_Num];
    uint8_t Hand_servo_on[Hand_Num];

    std::array<int, 16> R_Hand_j_pos;
    std::array<int, 16> R_Hand_j_cur;

    std::array<int, 16> L_Hand_j_pos;
    std::array<int, 16> L_Hand_j_cur;

    double Arm_j_pos[Arm_Num][Arm_DOF];
    double Arm_j_tar[Arm_Num][Arm_DOF];

    double Arm_j_vel[Arm_Num][Arm_DOF];     // Franka velocity
    double Arm_C_Pos[Arm_Num][16];          //Cartesian space pose (End-effector)
    double Arm_j_tq[Arm_Num][Arm_DOF];      // Franka torque

    franka::RobotState R_robot_state;
    std::array<double, 7> R_q;
    std::array<double, 7> R_qdes;
    std::array<double, 7> R_tau_d_last;
    std::array<double, 7> R_gravity;

    franka::RobotState L_robot_state;
    std::array<double, 7> L_q;
    std::array<double, 7> L_qdes;
    std::array<double, 7> L_tau_d_last;
    std::array<double, 7> L_gravity;

    bool franka_L_gripper_ishoming;
    bool franka_L_gripper_isgrasping;
    uint8_t franka_L_gripper_Mode;
    double franka_L_gripper_grasping_width;
    double franka_L_gripper_grasping_speed;
    double franka_L_gripper_grasping_force;
    double franka_L_gripper_current_width;

    std::atomic<int> process_num;
} SHMmsgs;


static const key_t shm_msg_key = 0x3940;
static const key_t shm_rd_key = 10334;

static void init_shm(int shm_key, int &shm_id_, SHMmsgs **shm_ref)
{
    // 기존 SHM 확인 및 크기 체크
    int existing_shm_id = shmget(shm_key, 0, 0);
    if (existing_shm_id != -1)
    {
        struct shmid_ds shm_info;
        if (shmctl(existing_shm_id, IPC_STAT, &shm_info) == 0)
        {
            if (shm_info.shm_segsz != sizeof(SHMmsgs))
            {
                printf("⚠️  기존 SHM 크기가 다릅니다! (기존: %zu bytes, 필요: %zu bytes)\n", 
                       shm_info.shm_segsz, sizeof(SHMmsgs));
                printf("기존 SHM을 제거하고 새로 생성합니다...\n");
                
                if (shm_info.shm_nattch > 0)
                {
                    printf("⚠️  경고: 기존 SHM에 %lu개의 프로세스가 연결되어 있습니다.\n", 
                           shm_info.shm_nattch);
                    printf("모든 프로세스를 종료한 후 다시 시도하세요.\n");
                    printf("또는 수동으로 제거: ipcrm -m %d\n", existing_shm_id);
                    exit(1);
                }
                
                if (shmctl(existing_shm_id, IPC_RMID, NULL) == -1)
                {
                    perror("❌ 기존 SHM 제거 실패");
                    exit(1);
                }
                printf("✅ 기존 SHM 제거 완료\n");
            }
            else
            {
                shm_id_ = existing_shm_id;
            }
        }
    }
    
    if (shm_id_ == 0)
    {
        if ((shm_id_ = shmget(shm_key, sizeof(SHMmsgs), IPC_CREAT | 0666)) == -1)
        {
            perror("❌ shmget failed");
            printf("SHM 키: 0x%x (십진수: %d)\n", shm_key, shm_key);
            printf("SHM 크기: %zu bytes\n", sizeof(SHMmsgs));
            exit(1);
        }
    }
    
    if ((*shm_ref = (SHMmsgs *)shmat(shm_id_, NULL, 0)) == (SHMmsgs *)-1)
    {
        perror("❌ shmat failed");
        exit(1);
    }

    // Clean Start 시 Hand_j_tar를 0으로 초기화 (손가락이 지멋대로 움직이는 것 방지)
    if ((*shm_ref)->process_num == 0)
    {
        printf("✅ Process num 0 ! Clean Start!\n");
        printf("🔄 Hand_j_tar 초기화 중...\n");
        
        // Hand 목표값을 0으로 초기화
        for (int h = 0; h < Hand_Num; h++)
        {
            for (int i = 0; i < Hand_DOF; i++)
            {
                (*shm_ref)->Hand_j_tar[h][i] = 0;
            }
            (*shm_ref)->Hand_CMD_Status[h] = false;
            (*shm_ref)->hand_movement_duration[h] = 0.0;
        }
        printf("✅ Hand_j_tar 초기화 완료 (모두 0으로 설정)\n");
    }

    (*shm_ref)->process_num++;
    printf("✅ Shared Memory 연결 성공 (shm_id: %d, process_num: %d, 크기: %zu bytes)\n", 
           shm_id_, (*shm_ref)->process_num.load(), sizeof(SHMmsgs));
}

static void deleteSharedMemory(int shm_id__, SHMmsgs *shm_ref)
{
    shm_ref->process_num--;
    if (shm_ref->process_num == 0)
    {
        printf("process num 0. removing shared memory\n");

        if (shmctl(shm_id__, IPC_RMID, NULL) == -1)
        {
            printf("shared memoty failed to remove. \n");
        }
        else
        {
            printf("Shared memory succesfully removed\n");
        }
    }
}