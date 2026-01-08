
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



static const key_t shm_msg_key = 0x8178;
static const key_t shm_rd_key = 10334;

static void init_shm(int shm_key, int &shm_id_, SHMmsgs **shm_ref)
{
    if ((shm_id_ = shmget(shm_key, sizeof(SHMmsgs), IPC_CREAT | 0666)) == -1)
    {
        printf("shm mtx failed\n");
        exit(0);
    }
    if ((*shm_ref = (SHMmsgs *)shmat(shm_id_, NULL, 0)) == (SHMmsgs *)-1)
    {
        printf("shmat failed\n");
        exit(0);
    }

    if ((*shm_ref)->process_num == 0)
    {
         printf("Process num 0 ! Clean Start!\n");
    }

    (*shm_ref)->process_num++;
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