
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
   
   thread_args3.id = 103;
   thread_args3.message = "FRANKA THREAD LEFT";

   thread_args4.id = 104;
   thread_args4.message = "FRANKA THREAD LEFT GRIPPER";

   thread_args5.id = 105;
   thread_args5.message = "PRINT_THREAD";

   pthread_create(&thread3, NULL, &franka_control_thread_L, (void *)&thread_args3);
   pthread_create(&thread4, NULL, &franka_control_thread_L_gripper, (void *)&thread_args4);
   //pthread_create(&thread5, NULL, &data_print_thread, (void *)&thread_args5);

   pthread_join(thread3, NULL);
   
   return 0;
}