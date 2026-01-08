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
#include <franka/active_control.h>
// #include "Predefined_Motion.h" // 양손 납땜
#include "Tillted_Test_Motion.h"  // 기울여서 오른손만 실험중
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


#define UDP_PORT 8888   
#define BUF_SIZE 1024   

int sockfd;

#pragma pack(push, 1) 
struct UDP_Request {
    double arm_targets[Arm_Num][Arm_DOF];
    int16_t hand_targets[Hand_Num][Hand_DOF];      
};

struct UDP_Response {
    double arm_positions[Arm_Num][Arm_DOF]; 
    int16_t hand_positions[Hand_Num][Hand_DOF];
};
#pragma pack(pop)


void *udp_server_thread(void *ptr)
{
    struct sockaddr_in server_addr, client_addr;
    char buffer[BUF_SIZE];
    socklen_t client_len = sizeof(client_addr);

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("❌ socket creation failed");
        pthread_exit(NULL);
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;           // IPv4
    server_addr.sin_addr.s_addr = INADDR_ANY;   // 모든 IP 주소에서 수신
    server_addr.sin_port = htons(UDP_PORT);     // 포트 번호 설정

    if (bind(sockfd, (const struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("❌ bind failed");
        close(sockfd);
        pthread_exit(NULL);
    }
    std::cout << "✅ UDP Server listening on port " << UDP_PORT << std::endl;

    while (true) 
    {
        ssize_t n = recvfrom(sockfd, buffer, BUF_SIZE, 0, (struct sockaddr *)&client_addr, &client_len);

        if (n != sizeof(UDP_Request)) {
            std::cerr << "Warning: Received malformed packet with size " << n << std::endl;
            continue; // 잘못된 패킷은 무시
        }

        UDP_Request* request = (UDP_Request*)buffer;
        memcpy(shm_msgs_->Arm_j_tar, request->arm_targets, sizeof(request->arm_targets));
        
        for(int i = 0; i < Hand_Num; ++i) {
            memcpy(shm_msgs_->Hand_j_tar[i], request->hand_targets[i], sizeof(request->hand_targets[i]));
        }

        UDP_Response response;
        memcpy(response.arm_positions, shm_msgs_->Arm_j_pos, sizeof(shm_msgs_->Arm_j_pos));
        memcpy(response.hand_positions, shm_msgs_->Hand_j_pos, sizeof(shm_msgs_->Hand_j_pos));
        
        sendto(sockfd, &response, sizeof(UDP_Response), 0,
                (const struct sockaddr *)&client_addr, client_len);
    }

    close(sockfd);
    return nullptr;
}
void delay_ms(unsigned long milisec)
{
    for (unsigned long i = 0; i < milisec; i++)
    {
        usleep(1000);
    }
}

void *franka_control_thread_R(void *ptr) //Frankas_control_thread_R
{
    try
    {
        double speed_factor = 0.3;
        double position_threshold = 0.01; // 10mm 이상 차이나면 이동 시작

        std::cout << "🔗 Connecting to Franka..." << std::endl;
        franka::Robot robot("172.16.0.1");
        std::cout << "✅ Connected to Franka at 172.16.0.1" << std::endl;
        robot.automaticErrorRecovery();

        setDefaultBehavior(robot);
        franka::RobotState initial_state = robot.readOnce();

        robot.setCollisionBehavior({{100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0}},
                                   {{100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0}},
                                   {{100.0, 100.0, 100.0, 100.0, 100.0, 100.0}},
                                   {{100.0, 100.0, 100.0, 100.0, 100.0, 100.0}});

        // 초기 target을 현재 위치로 설정
        for (int i = 0; i < Arm_DOF; i++) {
            shm_msgs_->Arm_j_tar[Arm_R][i] = initial_state.q[i];
            shm_msgs_->Arm_j_pos[Arm_R][i] = initial_state.q[i];
        }
        shm_msgs_->R_robot_state = initial_state;
        shm_msgs_->R_q = initial_state.q;
        
        std::cout << "🚀 SHM Target 모드 시작 (ROS2에서 /franka/arm_target/right로 목표 전송)" << std::endl;
        std::cout << "📍 현재 위치: [";
        for (int i = 0; i < Arm_DOF; i++) {
            std::cout << initial_state.q[i];
            if (i < Arm_DOF - 1) std::cout << ", ";
        }
        std::cout << "]" << std::endl;

        std::array<double, 7> last_target;
        for (int i = 0; i < Arm_DOF; i++) {
            last_target[i] = initial_state.q[i];
        }

        while (1)
        {
            // 현재 로봇 상태 읽기 및 SHM에 쓰기
            franka::RobotState robot_state = robot.readOnce();
            for (int i = 0; i < Arm_DOF; i++) {
                shm_msgs_->Arm_j_pos[Arm_R][i] = robot_state.q[i];
                shm_msgs_->Arm_j_tq[Arm_R][i] = robot_state.tau_J[i];
                shm_msgs_->Arm_j_vel[Arm_R][i] = robot_state.dq[i];
            }
            shm_msgs_->R_robot_state = robot_state;
            shm_msgs_->R_q = robot_state.q;

            // SHM의 target과 마지막 target 비교 (새로운 명령이 들어왔는지 확인)
            bool new_target = false;
            double max_diff = 0.0;
            for (int i = 0; i < Arm_DOF; i++) {
                double diff = std::abs(shm_msgs_->Arm_j_tar[Arm_R][i] - last_target[i]);
                if (diff > max_diff) max_diff = diff;
                if (diff > position_threshold) {
                    new_target = true;
                }
            }

            if (new_target)
            {
                // 새로운 target으로 이동
                std::array<double, 7> target_pose;
                for (int i = 0; i < Arm_DOF; i++) {
                    target_pose[i] = shm_msgs_->Arm_j_tar[Arm_R][i];
                    last_target[i] = shm_msgs_->Arm_j_tar[Arm_R][i];
                }

                std::cout << "🎯 새로운 Target 수신! 이동 시작..." << std::endl;
                std::cout << "   Target: [";
                for (int i = 0; i < Arm_DOF; i++) {
                    std::cout << std::fixed << std::setprecision(3) << target_pose[i];
                    if (i < Arm_DOF - 1) std::cout << ", ";
                }
                std::cout << "]" << std::endl;

                MotionGenerator motion_generator(speed_factor, target_pose);
                robot.control([&](const franka::RobotState& robot_state, franka::Duration period) -> franka::JointPositions {
                    // shm에 Franka 데이터 쓰기 (1kHz로 업데이트)
                    for (int i = 0; i < Arm_DOF; i++) {
                        shm_msgs_->Arm_j_pos[Arm_R][i] = robot_state.q[i];
                        shm_msgs_->Arm_j_tq[Arm_R][i] = robot_state.tau_J[i];
                        shm_msgs_->Arm_j_vel[Arm_R][i] = robot_state.dq[i];
                    }
                    shm_msgs_->R_robot_state = robot_state;
                    shm_msgs_->R_q = robot_state.q;
                    
                    return motion_generator(robot_state, period);
                });

                std::cout << "✅ Target 도달 완료!" << std::endl;
            }

            usleep(1000); // 1kHz = 1ms
        }
    }
    catch (const franka::Exception &e)
    {
        std::cerr << "❌ Franka control error: " << e.what() << std::endl;
    }
    return nullptr;
}

void *data_print_thread(void *ptr)
{
    while (1)
    {
        std::cout << "\r"
                  << "tau_measured [Nm]: " << shm_msgs_->R_robot_state.tau_J
                  << " Arm_Joint [rad]: " << shm_msgs_->R_robot_state.q
                  << " Hand_Joint [rad]: " << shm_msgs_->R_Hand_j_pos
                  << " Gripper_Width [mm]: " << shm_msgs_->franka_L_gripper_current_width;
        std::cout.flush();                 
        usleep(1000);
    }
}
/* RT EtherCAT thread */
void *ecatthread(void *ptr) //KISTAR_Hand_control_thread_R  
{
    struct timespec ts, tleft;
    int ht;
    int64 cycletime;

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
            kistar_tx.IN.Actuator_Status1 = 0xFFFF; //motor off: 0x0000, motor on: 0xFFFF
            kistar_tx.IN.Actuator_Status2 = 1; //mode 0 안움직이기, 1 position control, 2 current control

            // 핸드 제어: SHM의 Hand_j_tar를 그대로 JOINT_TARGET에 전송
            for (int i = 0; i < Hand_DOF; i++) 
            {
                kistar_tx.IN.JOINT_TARGET[i] = shm_msgs_->Hand_j_tar[Hand_R][i];
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
            
            // data save: Position, Tactile, Kinesthetic 정보만 SHM에 쓰기
            for (int i = 0; i < Hand_DOF; i++)
            {
                shm_msgs_->Hand_j_pos[Hand_R][i] = kistar_rx.OUT.Position[i];
                shm_msgs_->R_Hand_j_pos[i] = shm_msgs_->Hand_j_pos[Hand_R][i];
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
    if (ec_init("enp1s0f0"))
    {
        printf("ec_init on %s succeeded.\n", "enp1s0f0");
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
        printf("No socket connection on %s\nExcecute as root\n", "enp1s0f0");
    }
}

void signal_callback_handler(int signum)
{
    printf("Caught Ctrl + C!!");

    ec_close();
    printf("Terminating EtherCAT!! \n");
    bool_ethecat_loop = false;

    close(sockfd);

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