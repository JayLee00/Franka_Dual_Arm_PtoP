// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from kistar_hand_ros2:msg/HandState.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__HAND_STATE__BUILDER_HPP_
#define KISTAR_HAND_ROS2__MSG__DETAIL__HAND_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "kistar_hand_ros2/msg/detail/hand_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace kistar_hand_ros2
{

namespace msg
{

namespace builder
{

class Init_HandState_hand_id
{
public:
  explicit Init_HandState_hand_id(::kistar_hand_ros2::msg::HandState & msg)
  : msg_(msg)
  {}
  ::kistar_hand_ros2::msg::HandState hand_id(::kistar_hand_ros2::msg::HandState::_hand_id_type arg)
  {
    msg_.hand_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::kistar_hand_ros2::msg::HandState msg_;
};

class Init_HandState_tactile_sensors
{
public:
  explicit Init_HandState_tactile_sensors(::kistar_hand_ros2::msg::HandState & msg)
  : msg_(msg)
  {}
  Init_HandState_hand_id tactile_sensors(::kistar_hand_ros2::msg::HandState::_tactile_sensors_type arg)
  {
    msg_.tactile_sensors = std::move(arg);
    return Init_HandState_hand_id(msg_);
  }

private:
  ::kistar_hand_ros2::msg::HandState msg_;
};

class Init_HandState_kinesthetic_sensors
{
public:
  explicit Init_HandState_kinesthetic_sensors(::kistar_hand_ros2::msg::HandState & msg)
  : msg_(msg)
  {}
  Init_HandState_tactile_sensors kinesthetic_sensors(::kistar_hand_ros2::msg::HandState::_kinesthetic_sensors_type arg)
  {
    msg_.kinesthetic_sensors = std::move(arg);
    return Init_HandState_tactile_sensors(msg_);
  }

private:
  ::kistar_hand_ros2::msg::HandState msg_;
};

class Init_HandState_joint_positions
{
public:
  Init_HandState_joint_positions()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_HandState_kinesthetic_sensors joint_positions(::kistar_hand_ros2::msg::HandState::_joint_positions_type arg)
  {
    msg_.joint_positions = std::move(arg);
    return Init_HandState_kinesthetic_sensors(msg_);
  }

private:
  ::kistar_hand_ros2::msg::HandState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::kistar_hand_ros2::msg::HandState>()
{
  return kistar_hand_ros2::msg::builder::Init_HandState_joint_positions();
}

}  // namespace kistar_hand_ros2

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__HAND_STATE__BUILDER_HPP_
