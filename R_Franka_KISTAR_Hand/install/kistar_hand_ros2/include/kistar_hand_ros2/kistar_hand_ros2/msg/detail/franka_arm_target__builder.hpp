// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from kistar_hand_ros2:msg/FrankaArmTarget.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_TARGET__BUILDER_HPP_
#define KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_TARGET__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "kistar_hand_ros2/msg/detail/franka_arm_target__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace kistar_hand_ros2
{

namespace msg
{

namespace builder
{

class Init_FrankaArmTarget_arm_id
{
public:
  explicit Init_FrankaArmTarget_arm_id(::kistar_hand_ros2::msg::FrankaArmTarget & msg)
  : msg_(msg)
  {}
  ::kistar_hand_ros2::msg::FrankaArmTarget arm_id(::kistar_hand_ros2::msg::FrankaArmTarget::_arm_id_type arg)
  {
    msg_.arm_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::kistar_hand_ros2::msg::FrankaArmTarget msg_;
};

class Init_FrankaArmTarget_joint_targets
{
public:
  Init_FrankaArmTarget_joint_targets()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_FrankaArmTarget_arm_id joint_targets(::kistar_hand_ros2::msg::FrankaArmTarget::_joint_targets_type arg)
  {
    msg_.joint_targets = std::move(arg);
    return Init_FrankaArmTarget_arm_id(msg_);
  }

private:
  ::kistar_hand_ros2::msg::FrankaArmTarget msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::kistar_hand_ros2::msg::FrankaArmTarget>()
{
  return kistar_hand_ros2::msg::builder::Init_FrankaArmTarget_joint_targets();
}

}  // namespace kistar_hand_ros2

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_TARGET__BUILDER_HPP_
