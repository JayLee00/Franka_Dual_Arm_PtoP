// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from kistar_hand_ros2:msg/FrankaArmState.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_STATE__BUILDER_HPP_
#define KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "kistar_hand_ros2/msg/detail/franka_arm_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace kistar_hand_ros2
{

namespace msg
{

namespace builder
{

class Init_FrankaArmState_arm_id
{
public:
  explicit Init_FrankaArmState_arm_id(::kistar_hand_ros2::msg::FrankaArmState & msg)
  : msg_(msg)
  {}
  ::kistar_hand_ros2::msg::FrankaArmState arm_id(::kistar_hand_ros2::msg::FrankaArmState::_arm_id_type arg)
  {
    msg_.arm_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::kistar_hand_ros2::msg::FrankaArmState msg_;
};

class Init_FrankaArmState_joint_torques
{
public:
  explicit Init_FrankaArmState_joint_torques(::kistar_hand_ros2::msg::FrankaArmState & msg)
  : msg_(msg)
  {}
  Init_FrankaArmState_arm_id joint_torques(::kistar_hand_ros2::msg::FrankaArmState::_joint_torques_type arg)
  {
    msg_.joint_torques = std::move(arg);
    return Init_FrankaArmState_arm_id(msg_);
  }

private:
  ::kistar_hand_ros2::msg::FrankaArmState msg_;
};

class Init_FrankaArmState_joint_positions
{
public:
  Init_FrankaArmState_joint_positions()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_FrankaArmState_joint_torques joint_positions(::kistar_hand_ros2::msg::FrankaArmState::_joint_positions_type arg)
  {
    msg_.joint_positions = std::move(arg);
    return Init_FrankaArmState_joint_torques(msg_);
  }

private:
  ::kistar_hand_ros2::msg::FrankaArmState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::kistar_hand_ros2::msg::FrankaArmState>()
{
  return kistar_hand_ros2::msg::builder::Init_FrankaArmState_joint_positions();
}

}  // namespace kistar_hand_ros2

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_STATE__BUILDER_HPP_
