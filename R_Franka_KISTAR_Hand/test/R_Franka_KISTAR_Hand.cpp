
#include <sys/time.h>
#include <sched.h>
#include <string.h>
#include <pthread.h>
#include <math.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>
#include <stdio.h>
#include <iostream>
#include <unistd.h>


#include <Hand_Arm_Setting.h>

struct ThreadArgs {
    int id;
    std::string message;
};

ThreadArgs thread_args1, thread_args2, thread_args3, thread_args4, thread_args5, thread_args6;

int main(int argc, char *argv[])
{
   printf("Arm and Hand System Test \n");
   signal(SIGINT, signal_callback_handler);

   init_shm(shm_msg_key, shm_id, &shm_msgs_);
   if (shm_msgs_ == NULL)
   {
      // init_shm currently exits on failure, but this is good practice.
      fprintf(stderr, "FATAL: Shared memory initialization failed.\n");
      return EXIT_FAILURE;
   }
   else
   {
      fprintf(stderr, "Shared Memory Connection Success\n");
   }
   
   thread_args1.id = 101;
   thread_args1.message = "ECAT_THREAD";

   thread_args2.id = 102;
   thread_args2.message = "FRANKA THREAD RIGHT";

   thread_args5.id = 105;
   thread_args5.message = "PRINT_THREAD";

   thread_args6.id = 106;
   thread_args6.message = "UDP_SERVER_THREAD";

   //pthread_create(&thread6, NULL, &udp_server_thread, (void *)&thread_args6);

   // 프랑카 스레드 시작 (Arm 제어용)
   pthread_create(&thread3, NULL, &franka_control_thread_R, (void *)&thread_args2);
   
   // EtherCAT 스레드 시작 (Hand 제어용)
   pthread_create(&thread1, NULL, &ecatthread, (void *)&thread_args1);
   pthread_create(&thread2, NULL, &ecatcheck, NULL);
   ethercat_run();  // 이 함수가 블로킹되어 계속 실행됨
   
   // ethercat_run()이 블로킹이므로 join은 실행되지 않음
   // pthread_join(thread3, NULL);

   //pthread_join(thread6, NULL);
   
   return 0;
}