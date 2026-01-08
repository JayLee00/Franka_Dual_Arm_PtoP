#include <rclcpp/rclcpp.hpp>
#include <memory>
#include <chrono>
#include <thread>
#include <sys/ipc.h>
#include <sys/shm.h>
#include "kistar_hand/shm.h"
#include "kistar_hand_ros2/msg/franka_arm_state.hpp"
#include "kistar_hand_ros2/msg/franka_arm_target.hpp"
#include "kistar_hand_ros2/msg/hand_state.hpp"
#include "kistar_hand_ros2/msg/hand_target.hpp"

using namespace std::chrono_literals;

class ShmRos2Bridge : public rclcpp::Node
{
public:
    ShmRos2Bridge() : Node("shm_ros2_bridge")
    {
        // Shared Memory 초기화
        init_shm(shm_msg_key, shm_id_, &shm_msgs_);
        if (shm_msgs_ == nullptr)
        {
            RCLCPP_FATAL(this->get_logger(), "Shared memory initialization failed!");
            rclcpp::shutdown();
            return;
        }
        RCLCPP_INFO(this->get_logger(), "✅ Shared Memory 연결 성공");

        // Publishers (shm -> ROS2)
        // Franka Arm State Publishers
        pub_franka_arm_state_R_ = this->create_publisher<kistar_hand_ros2::msg::FrankaArmState>(
            "franka/arm_state/right", 10);
        pub_franka_arm_state_L_ = this->create_publisher<kistar_hand_ros2::msg::FrankaArmState>(
            "franka/arm_state/left", 10);

        // Hand State Publishers
        pub_hand_state_R_ = this->create_publisher<kistar_hand_ros2::msg::HandState>(
            "hand/state/right", 10);
        pub_hand_state_L_ = this->create_publisher<kistar_hand_ros2::msg::HandState>(
            "hand/state/left", 10);

        // Subscribers (ROS2 -> shm)
        // Franka Arm Target Subscribers
        sub_franka_arm_target_R_ = this->create_subscription<kistar_hand_ros2::msg::FrankaArmTarget>(
            "franka/arm_target/right", 10,
            std::bind(&ShmRos2Bridge::frankaArmTargetCallback_R, this, std::placeholders::_1));
        sub_franka_arm_target_L_ = this->create_subscription<kistar_hand_ros2::msg::FrankaArmTarget>(
            "franka/arm_target/left", 10,
            std::bind(&ShmRos2Bridge::frankaArmTargetCallback_L, this, std::placeholders::_1));

        // Hand Target Subscribers
        sub_hand_target_R_ = this->create_subscription<kistar_hand_ros2::msg::HandTarget>(
            "hand/target/right", 10,
            std::bind(&ShmRos2Bridge::handTargetCallback_R, this, std::placeholders::_1));
        sub_hand_target_L_ = this->create_subscription<kistar_hand_ros2::msg::HandTarget>(
            "hand/target/left", 10,
            std::bind(&ShmRos2Bridge::handTargetCallback_L, this, std::placeholders::_1));

        // Timer for publishing state (100Hz = 10ms)
        timer_ = this->create_wall_timer(
            10ms, std::bind(&ShmRos2Bridge::publishStates, this));

        RCLCPP_INFO(this->get_logger(), "🚀 ROS2-SHM Bridge 노드 시작됨");
    }

    ~ShmRos2Bridge()
    {
        if (shm_msgs_ != nullptr)
        {
            deleteSharedMemory(shm_id_, shm_msgs_);
        }
    }

private:
    void publishStates()
    {
        // Franka Right Arm State
        auto msg_franka_R = kistar_hand_ros2::msg::FrankaArmState();
        msg_franka_R.arm_id = Arm_R;
        for (int i = 0; i < Arm_DOF; i++)
        {
            msg_franka_R.joint_positions[i] = shm_msgs_->Arm_j_pos[Arm_R][i];
            msg_franka_R.joint_torques[i] = shm_msgs_->Arm_j_tq[Arm_R][i];
        }
        pub_franka_arm_state_R_->publish(msg_franka_R);

        // Franka Left Arm State
        auto msg_franka_L = kistar_hand_ros2::msg::FrankaArmState();
        msg_franka_L.arm_id = Arm_L;
        for (int i = 0; i < Arm_DOF; i++)
        {
            msg_franka_L.joint_positions[i] = shm_msgs_->Arm_j_pos[Arm_L][i];
            msg_franka_L.joint_torques[i] = shm_msgs_->Arm_j_tq[Arm_L][i];
        }
        pub_franka_arm_state_L_->publish(msg_franka_L);

        // Hand Right State
        auto msg_hand_R = kistar_hand_ros2::msg::HandState();
        msg_hand_R.hand_id = Hand_R;
        for (int i = 0; i < Hand_DOF; i++)
        {
            msg_hand_R.joint_positions[i] = shm_msgs_->Hand_j_pos[Hand_R][i];
        }
        for (int i = 0; i < Kinesthetic_Sensor_DATA_NUM; i++)
        {
            msg_hand_R.kinesthetic_sensors[i] = shm_msgs_->Hand_j_kin[Hand_R][i];
        }
        for (int i = 0; i < Tactile_Sensor_DATA_NUM; i++)
        {
            msg_hand_R.tactile_sensors[i] = shm_msgs_->Hand_j_tac[Hand_R][i];
        }
        pub_hand_state_R_->publish(msg_hand_R);

        // Hand Left State
        auto msg_hand_L = kistar_hand_ros2::msg::HandState();
        msg_hand_L.hand_id = Hand_L;
        for (int i = 0; i < Hand_DOF; i++)
        {
            msg_hand_L.joint_positions[i] = shm_msgs_->Hand_j_pos[Hand_L][i];
        }
        for (int i = 0; i < Kinesthetic_Sensor_DATA_NUM; i++)
        {
            msg_hand_L.kinesthetic_sensors[i] = shm_msgs_->Hand_j_kin[Hand_L][i];
        }
        for (int i = 0; i < Tactile_Sensor_DATA_NUM; i++)
        {
            msg_hand_L.tactile_sensors[i] = shm_msgs_->Hand_j_tac[Hand_L][i];
        }
        pub_hand_state_L_->publish(msg_hand_L);
    }

    void frankaArmTargetCallback_R(const kistar_hand_ros2::msg::FrankaArmTarget::SharedPtr msg)
    {
        // arm_id 체크 없이 항상 Right로 처리 (토픽 자체가 right이므로)
        RCLCPP_INFO(this->get_logger(), "📥 Arm Target R 수신! arm_id=%d", msg->arm_id);
        for (int i = 0; i < Arm_DOF; i++)
        {
            shm_msgs_->Arm_j_tar[Arm_R][i] = msg->joint_targets[i];
        }
        RCLCPP_INFO(this->get_logger(), "   Target[0]: %.4f, Target[1]: %.4f", 
                    shm_msgs_->Arm_j_tar[Arm_R][0], shm_msgs_->Arm_j_tar[Arm_R][1]);
    }

    void frankaArmTargetCallback_L(const kistar_hand_ros2::msg::FrankaArmTarget::SharedPtr msg)
    {
        if (msg->arm_id == Arm_L)
        {
            for (int i = 0; i < Arm_DOF; i++)
            {
                shm_msgs_->Arm_j_tar[Arm_L][i] = msg->joint_targets[i];
            }
        }
    }

    void handTargetCallback_R(const kistar_hand_ros2::msg::HandTarget::SharedPtr msg)
    {
        if (msg->hand_id == Hand_R)
        {
            shm_msgs_->Hand_CMD_Status[Hand_R] = true;
            shm_msgs_->hand_movement_duration[Hand_R] = msg->movement_duration;
            for (int i = 0; i < Hand_DOF; i++)
            {
                shm_msgs_->Hand_j_tar[Hand_R][i] = msg->joint_targets[i];
            }
        }
    }

    void handTargetCallback_L(const kistar_hand_ros2::msg::HandTarget::SharedPtr msg)
    {
        if (msg->hand_id == Hand_L)
        {
            shm_msgs_->Hand_CMD_Status[Hand_L] = true;
            shm_msgs_->hand_movement_duration[Hand_L] = msg->movement_duration;
            for (int i = 0; i < Hand_DOF; i++)
            {
                shm_msgs_->Hand_j_tar[Hand_L][i] = msg->joint_targets[i];
            }
        }
    }

    // Shared Memory
    int shm_id_;
    SHMmsgs *shm_msgs_;

    // Publishers
    rclcpp::Publisher<kistar_hand_ros2::msg::FrankaArmState>::SharedPtr pub_franka_arm_state_R_;
    rclcpp::Publisher<kistar_hand_ros2::msg::FrankaArmState>::SharedPtr pub_franka_arm_state_L_;
    rclcpp::Publisher<kistar_hand_ros2::msg::HandState>::SharedPtr pub_hand_state_R_;
    rclcpp::Publisher<kistar_hand_ros2::msg::HandState>::SharedPtr pub_hand_state_L_;

    // Subscribers
    rclcpp::Subscription<kistar_hand_ros2::msg::FrankaArmTarget>::SharedPtr sub_franka_arm_target_R_;
    rclcpp::Subscription<kistar_hand_ros2::msg::FrankaArmTarget>::SharedPtr sub_franka_arm_target_L_;
    rclcpp::Subscription<kistar_hand_ros2::msg::HandTarget>::SharedPtr sub_hand_target_R_;
    rclcpp::Subscription<kistar_hand_ros2::msg::HandTarget>::SharedPtr sub_hand_target_L_;

    // Timer
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ShmRos2Bridge>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

