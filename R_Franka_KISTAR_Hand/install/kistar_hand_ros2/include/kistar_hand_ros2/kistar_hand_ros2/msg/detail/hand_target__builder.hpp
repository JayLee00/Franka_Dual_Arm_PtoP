// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from kistar_hand_ros2:msg/HandTarget.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__BUILDER_HPP_
#define KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "kistar_hand_ros2/msg/detail/hand_target__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace kistar_hand_ros2
{

namespace msg
{

namespace builder
{

class Init_HandTarget_hand_id
{
public:
  explicit Init_HandTarget_hand_id(::kistar_hand_ros2::msg::HandTarget & msg)
  : msg_(msg)
  {}
  ::kistar_hand_ros2::msg::HandTarget hand_id(::kistar_hand_ros2::msg::HandTarget::_hand_id_type arg)
  {
    msg_.hand_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::kistar_hand_ros2::msg::HandTarget msg_;
};

class Init_HandTarget_movement_duration
{
public:
  explicit Init_HandTarget_movement_duration(::kistar_hand_ros2::msg::HandTarget & msg)
  : msg_(msg)
  {}
  Init_HandTarget_hand_id movement_duration(::kistar_hand_ros2::msg::HandTarget::_movement_duration_type arg)
  {
    msg_.movement_duration = std::move(arg);
    return Init_HandTarget_hand_id(msg_);
  }

private:
  ::kistar_hand_ros2::msg::HandTarget msg_;
};

class Init_HandTarget_joint_targets
{
public:
  Init_HandTarget_joint_targets()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_HandTarget_movement_duration joint_targets(::kistar_hand_ros2::msg::HandTarget::_joint_targets_type arg)
  {
    msg_.joint_targets = std::move(arg);
    return Init_HandTarget_movement_duration(msg_);
  }

private:
  ::kistar_hand_ros2::msg::HandTarget msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::kistar_hand_ros2::msg::HandTarget>()
{
  return kistar_hand_ros2::msg::builder::Init_HandTarget_joint_targets();
}

}  // namespace kistar_hand_ros2

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__BUILDER_HPP_
