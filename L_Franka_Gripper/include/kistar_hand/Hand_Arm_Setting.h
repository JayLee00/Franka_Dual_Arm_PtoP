#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/time.h>
#include <sched.h>
#include <string.h>
#include <pthread.h>
#include <math.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <signal.h>
#include <iostream>
#include <iterator>
#include <cstdlib>
#include <iomanip>
#include <cmath>
#include <chrono>
#include <mutex>
#include <thread>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <ethercattype.h>
#include "nicdrv.h"
#include "ethercatbase.h"
#include "ethercatmain.h"
#include "ethercatdc.h"
#include "ethercatcoe.h"
#include "ethercatfoe.h"
#include "ethercatconfig.h"
#include "ethercatprint.h"
#include "shm.h"

#include <franka/duration.h>
#include <franka/exception.h>
#include <franka/model.h>
#include <franka/rate_limiting.h>
#include <franka/robot.h>
#include <franka/gripper.h>

#include "examples_common.h"

namespace {
template <class T, size_t N>
std::ostream& operator<<(std::ostream& ostream, const std::array<T, N>& array) {
  ostream << "[";
  std::copy(array.cbegin(), array.cend() - 1, std::ostream_iterator<T>(ostream, ","));
  std::copy(array.cend() - 1, array.cend(), std::ostream_iterator<T>(ostream));
  ostream << "]";
  return ostream;
}
}


#define NSEC_PER_SEC 1000000000
#define EC_TIMEOUTMON 500
#define PERIOD_NS 1000000
#define SEC_IN_NSEC 1000000000
#define HAND_NUM 1

#define Hand_Data_Read_Byte_Num 128
#define Hand_Data_Write_Byte_Num 64


double time_for_display = 0.0;
double time_for_display_franka = 0.0;
struct sched_param schedp;
char IOmap[4096];
pthread_t thread1, thread2, thread3, thread4, thread5, thread6;
struct timeval tv, t1, t2;
int deltat, tmax = 0;
int64 toff, gl_delta;
int DCdiff;
int os;
int dorun;
uint8 ob;
uint16 ob2;
uint8 *digout = 0;
int expectedWKC;
boolean needlf;
volatile int wkc;
uint8 currentgroup = 0;
bool bool_ethecat_loop = true;

typedef union
{
    uint8_t Byte[256];
    struct
    {
        uint16_t Actuator_Status1; // 2
        uint16_t Actuator_Status2; // 2

        int16_t Position[16];    // 32
        int16_t Current[16];     // 32
        int16_t Kinesthetic[12]; // 24
        int16_t Tactile[60];     // 120
        int16_t ADD_INFO[22];    // 44

    } OUT;
} Robot_Hand_Data; // Hand to PC

typedef union
{
    uint8_t Byte[64];
    struct
    {
        uint16_t Actuator_Status1; // 2
        uint16_t Actuator_Status2; // 2

        int16_t JOINT_TARGET[16]; // 32
        int16_t ADD_INFO[14];     // 28
    } IN;
} Robot_Hand_Command; // PC to Hand

SHMmsgs *shm_msgs_;
int shm_id;
bool is_initialized_franka;
Robot_Hand_Data kistar_rx;
Robot_Hand_Command kistar_tx;

std::atomic_bool running_franka_thread_R{true};
std::atomic_bool running_franka_thread_L{true};

void signal_callback_handler(int signum);
void add_timespec(struct timespec *ts, int64 addtime);
void ec_sync(int64 reftime, int64 cycletime, int64 *offsettime);
void ethercat_run();

void Robot_Hand_Motion(int16_t *R_Data, double duration)
{
    shm_msgs_->Hand_CMD_Status[0] = true;
    shm_msgs_->hand_movement_duration[0] = duration;
    for (int i = 0; i < 16; i++)
    {
        shm_msgs_->Hand_j_tar[0][i] = R_Data[i];
    }
}

void *franka_control_thread_L(void *ptr)
{
    try
    {
        std::cout << "🔗 Connecting to Franka..." << std::endl;
        franka::Robot robot("172.16.1.2");
        std::cout << "✅ Connected to Franka at 172.16.1.2" << std::endl;
        robot.automaticErrorRecovery();

        setDefaultBehavior(robot);
        franka::RobotState initial_state = robot.readOnce();

        
        MotionGenerator motion_generator(0.4, shm_msgs_->L_qdes);
        std::cout << "🚀 Moving to safe position..." << std::endl;
        robot.control(motion_generator);
        std::cout << "✅ Reached safe position!" << std::endl;

        robot.setCollisionBehavior({{100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0}},
                                   {{100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0}},
                                   {{100.0, 100.0, 100.0, 100.0, 100.0, 100.0}},
                                   {{100.0, 100.0, 100.0, 100.0, 100.0, 100.0}});

        double speed_factor = 0.4;

        while (1) // 1kHz Loop
        {
            MotionGenerator motion_generator(speed_factor, shm_msgs_->L_qdes);
            robot.control(motion_generator);
            
            //std::cout << "✅ Motion #" << shm_msgs_->Motion_Sequence << " finished." << std::endl;
            //std::cout <<  shm_msgs_->L_qdes << std::endl;
            std::cout << "✅ Motion #" << shm_msgs_->Motion_Sequence << " finished." << std::endl;
            std::cout << "✅ Gripper command for mode " << shm_msgs_->franka_L_gripper_Mode << " finished." << std::endl;
            usleep(1000);
        }
    }
    catch (const franka::Exception &e)
    {
        std::cerr << "❌ Franka control error: " << e.what() << std::endl;
    }
    return nullptr;
}

void *franka_control_thread_L_gripper(void *ptr)
{
    shm_msgs_->franka_L_gripper_ishoming = false;
    try
    {
        shm_msgs_->franka_L_gripper_isgrasping = false;
        shm_msgs_->franka_L_gripper_Mode = 0;
        shm_msgs_->franka_L_gripper_grasping_speed = 0.5;

        franka::Gripper gripper("172.16.1.2");

        if (!shm_msgs_->franka_L_gripper_ishoming)
        {
            shm_msgs_->franka_L_gripper_ishoming = true;
            // Do a homing in order to estimate the maximum grasping width with the current fingers.
            gripper.homing();
        }

        gripper.move(0.05, 0.5);
        int last_mode = -1;
        // Check for the maximum grasping width.
        franka::GripperState gripper_state = gripper.readOnce();
        while (1)
        {
            int current_mode = shm_msgs_->franka_L_gripper_Mode;
            if (gripper_state.max_width < shm_msgs_->franka_L_gripper_grasping_width)
            {
                std::cout << "Object is too large for the current fingers on the gripper." << std::endl;
            }
            if (current_mode != last_mode)
            {
                switch (shm_msgs_->franka_L_gripper_Mode)
                {
                case 0: // Initial position
                    shm_msgs_->franka_L_gripper_grasping_width = 0.05;
                    std::cout << "Large Open" << std::endl;
                    gripper.move(shm_msgs_->franka_L_gripper_grasping_width, shm_msgs_->franka_L_gripper_grasping_speed);
                    break;
                case 1: // Grasping
                    shm_msgs_->franka_L_gripper_grasping_width = 0.0005;
                    shm_msgs_->franka_L_gripper_grasping_force = 60;
                    std::cout << "Grasping" << std::endl;
                    gripper.grasp(shm_msgs_->franka_L_gripper_grasping_width, shm_msgs_->franka_L_gripper_grasping_speed, shm_msgs_->franka_L_gripper_grasping_force, 0.00, 0.01);
                    break;
                case 2: // Small Open
                    shm_msgs_->franka_L_gripper_grasping_width = 0.005;
                    std::cout << "Small Open" << std::endl;
                    gripper.move(shm_msgs_->franka_L_gripper_grasping_width, shm_msgs_->franka_L_gripper_grasping_speed);
                    break;
                case 3: // Large Open
                    shm_msgs_->franka_L_gripper_grasping_width = 0.02;
                    std::cout << "Large Open" << std::endl;
                    gripper.move(shm_msgs_->franka_L_gripper_grasping_width, shm_msgs_->franka_L_gripper_grasping_speed);
                    break;
                default:
                    break;
                }
                
                last_mode = current_mode;
                
            }
            //gripper_state = gripper.readOnce();
            usleep(1000);
        }
    }
    catch (franka::Exception const &e)
    {
        std::cout << e.what() << std::endl;
    }

    return nullptr;
}


void *data_print_thread(void *ptr)
{
    while (1)
    {
        std::cout << "\r"
                  << "tau_measured [Nm]: " << shm_msgs_->L_robot_state.tau_J
                  << " Arm_Joint [rad]: " << shm_msgs_->L_robot_state.q
                  << " Hand_Joint [rad]: " << shm_msgs_->L_Hand_j_pos
                  << " Gripper_Width [mm]: " << shm_msgs_->franka_L_gripper_current_width;
        std::cout.flush();                 
        usleep(1000);
    }
}
/* RT EtherCAT thread */
void *ecatthread(void *ptr)
{
    struct timespec ts, tleft;
    int ht;
    int64 cycletime;
    static double hand_start_pos[Hand_Num][Hand_DOF];
    static double hand_final_target[Hand_Num][Hand_DOF];
    static double hand_movement_duration[Hand_Num];
    static double hand_elapsed_time[Hand_Num];
    const double cycle_time_sec = (double)PERIOD_NS / NSEC_PER_SEC; // 0.001초

    clock_gettime(CLOCK_MONOTONIC, &ts);
    ht = (ts.tv_nsec / 1000000) + 1; /* round to nearest ms */
    ts.tv_nsec = ht * 1000000;
    cycletime = *(int *)ptr * 1000; /* cycletime in ns */
    toff = 0;
    dorun = 0;

    ec_send_processdata();
    add_timespec(&ts, cycletime + toff);
    time_for_display = ht;
    /* wait to cycle start */
    clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &ts, &tleft);
    while (1)
    {
        /* calculate next cycle start */
        add_timespec(&ts, cycletime + toff);
        time_for_display = ht;
        /* wait to cycle start */
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &ts, &tleft);
        if (dorun > 0)
        {
            wkc = ec_receive_processdata(EC_TIMEOUTRET);

            dorun++;

            // [수정] 핸드 제어 로직 전체 변경
            for (int h_idx = 0; h_idx < 1; h_idx++) 
            {
                // 1. 새로운 명령 감지
                if (shm_msgs_->Hand_CMD_Status[h_idx]) 
                {
                    // 보간 상태 초기화
                    hand_elapsed_time[h_idx] = 0.0;
                    hand_movement_duration[h_idx] = shm_msgs_->hand_movement_duration[h_idx];

                    for (int i = 0; i < Hand_DOF; i++) 
                    {
                        // 현재 위치를 시작점으로, 새 목표를 최종 목표로 설정
                        hand_start_pos[h_idx][i] = (double)shm_msgs_->Hand_j_pos[h_idx][i];
                        hand_final_target[h_idx][i] = (double)shm_msgs_->Hand_j_tar[h_idx][i];
                    }
                    
                    // 명령 처리 완료 플래그
                    shm_msgs_->Hand_CMD_Status[h_idx] = false;
                }

                // 2. 매 사이클마다 보간 수행
                hand_elapsed_time[h_idx] += cycle_time_sec;

                // 보간 비율 계산 (0.0 ~ 1.0)
                double alpha = hand_elapsed_time[h_idx] / shm_msgs_->hand_movement_duration[h_idx];
                if (alpha > 1.0) {
                    alpha = 1.0;
                }
                if (alpha < 0.0) {
                    alpha = 0.0;
                }

                // 3. 현재 스텝의 목표 각도 계산 및 명령 전송
                for (int i = 0; i < Hand_DOF; i++) 
                {
                    // 선형 보간: current = start + alpha * (end - start)
                    double current_target = hand_start_pos[h_idx][i] + alpha * (hand_final_target[h_idx][i] - hand_start_pos[h_idx][i]);
                    kistar_tx.IN.JOINT_TARGET[i] = (int16_t)current_target;
                }
            }
            // write data to ethercat
            for (int d_l = 0; d_l < Hand_Data_Write_Byte_Num; d_l++)
            {
                ec_slave[0].outputs[d_l] = kistar_tx.Byte[d_l];
            }
            // read data from ethercat
            for (int d_l = 0; d_l < Hand_Data_Read_Byte_Num; d_l++)
            {
                kistar_rx.Byte[d_l] = ec_slave[0].inputs[d_l];
            }
            // data save
            for (int i = 0; i < Hand_DOF; i++)
            {
                shm_msgs_->Hand_j_pos[Hand_R][i] = kistar_rx.OUT.Position[i];
                shm_msgs_->R_Hand_j_pos[i] = shm_msgs_->Hand_j_pos[Hand_R][i];
                shm_msgs_->Hand_j_cur[Hand_R][i] = kistar_rx.OUT.Current[i];
            }
            for (int i = 0; i < Kinesthetic_Sensor_DATA_NUM; i++)
            {
                shm_msgs_->Hand_j_kin[Hand_R][i] = kistar_rx.OUT.Kinesthetic[i];
            }
            for (int i = 0; i < Tactile_Sensor_DATA_NUM; i++)
            {
                shm_msgs_->Hand_j_tac[Hand_R][i] = kistar_rx.OUT.Tactile[i];
            }
            /*
                    printf(" J:");
                    for (int i = 0; i < Hand_DOF; i++)
                    {
                        printf(" %d ", (shm_msgs_->Hand_j_pos[Hand_R][i]));
                    }
                    printf(" FT:");
                    for (int i = 0; i < Kinesthetic_Sensor_DATA_NUM; i++)
                    {
                        printf(" %d ", (shm_msgs_->Hand_j_kin[Hand_R][i]));
                        printf(" %d ", (shm_msgs_->Hand_j_kin[Hand_R][i]));
                    }
                    printf("\n");
            */
            /* if we have some digital output, cycle */
            if (digout)
                *digout = (uint8)((dorun / 16) & 0xff);

            if (ec_slave[0].hasdc)
            {
                /* calulate toff to get linux time and DC synced */
                ec_sync(ec_DCtime, cycletime, &toff);
            }
            ec_send_processdata();
        }
    }
}

void *ecatcheck(void *ptr)
{
    int slave;

    while (1)
    {
        if (((wkc < expectedWKC) || ec_group[currentgroup].docheckstate))
        {
            if (needlf)
            {
                needlf = FALSE;
                printf("\n");
            }
            /* one ore more slaves are not responding */
            ec_group[currentgroup].docheckstate = FALSE;
            ec_readstate();
            for (slave = 1; slave <= ec_slavecount; slave++)
            {
                if ((ec_slave[slave].group == currentgroup) && (ec_slave[slave].state != EC_STATE_OPERATIONAL))
                {
                    ec_group[currentgroup].docheckstate = TRUE;
                    if (ec_slave[slave].state == (EC_STATE_SAFE_OP + EC_STATE_ERROR))
                    {
                        printf("ERROR : slave %d is in SAFE_OP + ERROR, attempting ack.\n", slave);
                        ec_slave[slave].state = (EC_STATE_SAFE_OP + EC_STATE_ACK);
                        ec_writestate(slave);
                    }
                    else if (ec_slave[slave].state == EC_STATE_SAFE_OP)
                    {
                        printf("WARNING : slave %d is in SAFE_OP, change to OPERATIONAL.\n", slave);
                        ec_slave[slave].state = EC_STATE_OPERATIONAL;
                        ec_writestate(slave);
                    }
                    else if (ec_slave[slave].state > EC_STATE_NONE)
                    {
                        if (ec_reconfig_slave(slave, EC_TIMEOUTMON))
                        {
                            ec_slave[slave].islost = FALSE;
                            printf("MESSAGE : slave %d reconfigured\n", slave);
                        }
                    }
                    else if (!ec_slave[slave].islost)
                    {
                        /* re-check state */
                        ec_statecheck(slave, EC_STATE_OPERATIONAL, EC_TIMEOUTRET);
                        if (ec_slave[slave].state == EC_STATE_NONE)
                        {
                            ec_slave[slave].islost = TRUE;
                            printf("ERROR : slave %d lost\n", slave);
                        }
                    }
                }
                if (ec_slave[slave].islost)
                {
                    if (ec_slave[slave].state == EC_STATE_NONE)
                    {
                        if (ec_recover_slave(slave, EC_TIMEOUTMON))
                        {
                            ec_slave[slave].islost = FALSE;
                            printf("MESSAGE : slave %d recovered\n", slave);
                        }
                    }
                    else
                    {
                        ec_slave[slave].islost = FALSE;
                        printf("MESSAGE : slave %d found\n", slave);
                    }
                }
            }
            if (!ec_group[currentgroup].docheckstate)
            {
                //printf("OK : all slaves resumed OPERATIONAL.\n");
            }
                
        }
        osal_usleep(10000);
    }
}

void ethercat_run()
{
    /* initialise SOEM, bind socket to ifname */
    if (ec_init("enp4s0"))
    {
        printf("ec_init on %s succeeded.\n", "enp4s0");
        /* find and auto-config slaves */
        if (ec_config(FALSE, &IOmap) > 0)
        {
            /* configure DC options for every DC capable slave found in the list */
            ec_configdc();

            printf("%d slaves found and configured.\n", ec_slavecount);
            /* wait for all slaves to reach SAFE_OP state */
            ec_statecheck(0, EC_STATE_SAFE_OP, EC_TIMEOUTSTATE);

            /* read indevidual slave state and store in ec_slave[] */
            ec_readstate();

            for (int cnt = 1; cnt <= ec_slavecount; cnt++)
            {
                printf("Slave:%d Name:%s Output size:%3d bits Input size:%3d bits State:%2d delay:%d hasdc:%d\n",
                       cnt, ec_slave[cnt].name, ec_slave[cnt].Obits, ec_slave[cnt].Ibits,
                       ec_slave[cnt].state, (int)ec_slave[cnt].pdelay, ec_slave[cnt].hasdc);
                /* check for EL2004 or EL2008 */
                if (!digout && ((ec_slave[cnt].eep_id == 0x0af83052) || (ec_slave[cnt].eep_id == 0x07d83052)))
                {
                    digout = ec_slave[cnt].outputs;
                }
            }

            expectedWKC = (ec_group[0].outputsWKC * 2) + ec_group[0].inputsWKC;
            if (expectedWKC != 3 * HAND_NUM)
            {
                printf("WARNING : Calculated Workcounter insufficient!");
            }
            else
            {
                printf("Calculated workcounter %d\n", expectedWKC);
            }

            printf("Request operational state for all slaves\n");
            ec_slave[0].state = EC_STATE_OPERATIONAL;
            ec_writestate(0); /* request OP state for all slaves */
            dorun = 1;
            /* activate cyclic process data */
            /* wait for all slaves to reach OP state */
            ec_statecheck(0, EC_STATE_OPERATIONAL, 5 * EC_TIMEOUTSTATE);

            if (ec_slave[0].state == EC_STATE_OPERATIONAL)
            {
                printf("Operational state reached for all slaves.\n");
                printf("Operation Start");
                fflush(stdout);
                osal_usleep(20000);

                while (bool_ethecat_loop)
                {
                }
            }
            else
            {
                printf("Not all slaves reached operational state.\n");
                ec_readstate();
                for (int i = 1; i <= ec_slavecount; i++)
                {
                    if (ec_slave[i].state != EC_STATE_OPERATIONAL)
                    {
                        printf("Slave %d State=0x%2.2x StatusCode=0x%4.4x : %s\n",
                               i, ec_slave[i].state, ec_slave[i].ALstatuscode, ec_ALstatuscode2string(ec_slave[i].ALstatuscode));
                    }
                }
            }
            printf("Request safe operational state for all slaves\n");
            ec_slave[0].state = EC_STATE_SAFE_OP;
            /* request SAFE_OP state for all slaves */
            ec_writestate(0);
        }
        else
        {
            printf("No slaves found!\n");
            ec_close();
        }
    }
    else
    {
        printf("No socket connection on %s\nExcecute as root\n", "enp4s0");
    }
}

void signal_callback_handler(int signum)
{
    printf("Caught Ctrl + C!!");

    deleteSharedMemory(shm_id, shm_msgs_);
    // Terminate program
    exit(signum);
}

/* add ns to timespec */
void add_timespec(struct timespec *ts, int64 addtime)
{
    int64 sec, nsec;

    nsec = addtime % NSEC_PER_SEC;
    sec = (addtime - nsec) / NSEC_PER_SEC;
    ts->tv_sec += sec;
    ts->tv_nsec += nsec;
    if (ts->tv_nsec > NSEC_PER_SEC)
    {
        nsec = ts->tv_nsec % NSEC_PER_SEC;
        ts->tv_sec += (ts->tv_nsec - nsec) / NSEC_PER_SEC;
        ts->tv_nsec = nsec;
    }
}

/* PI calculation to get linux time synced to DC time */
void ec_sync(int64 reftime, int64 cycletime, int64 *offsettime)
{
    static int64 integral = 0;
    int64 delta;
    /* set linux sync point 50us later than DC sync, just as example */
    delta = (reftime - 50000) % cycletime;
    if (delta > (cycletime / 2))
    {
        delta = delta - cycletime;
    }
    if (delta > 0)
    {
        integral++;
    }
    if (delta < 0)
    {
        integral--;
    }
    *offsettime = -(delta / 100) - (integral / 20);
    gl_delta = delta;
}