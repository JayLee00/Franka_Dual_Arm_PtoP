// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from kistar_hand_ros2:msg/HandTarget.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__TRAITS_HPP_
#define KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "kistar_hand_ros2/msg/detail/hand_target__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace kistar_hand_ros2
{

namespace msg
{

inline void to_flow_style_yaml(
  const HandTarget & msg,
  std::ostream & out)
{
  out << "{";
  // member: joint_targets
  {
    if (msg.joint_targets.size() == 0) {
      out << "joint_targets: []";
    } else {
      out << "joint_targets: [";
      size_t pending_items = msg.joint_targets.size();
      for (auto item : msg.joint_targets) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: movement_duration
  {
    out << "movement_duration: ";
    rosidl_generator_traits::value_to_yaml(msg.movement_duration, out);
    out << ", ";
  }

  // member: hand_id
  {
    out << "hand_id: ";
    rosidl_generator_traits::value_to_yaml(msg.hand_id, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const HandTarget & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: joint_targets
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.joint_targets.size() == 0) {
      out << "joint_targets: []\n";
    } else {
      out << "joint_targets:\n";
      for (auto item : msg.joint_targets) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: movement_duration
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "movement_duration: ";
    rosidl_generator_traits::value_to_yaml(msg.movement_duration, out);
    out << "\n";
  }

  // member: hand_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "hand_id: ";
    rosidl_generator_traits::value_to_yaml(msg.hand_id, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const HandTarget & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace kistar_hand_ros2

namespace rosidl_generator_traits
{

[[deprecated("use kistar_hand_ros2::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const kistar_hand_ros2::msg::HandTarget & msg,
  std::ostream & out, size_t indentation = 0)
{
  kistar_hand_ros2::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use kistar_hand_ros2::msg::to_yaml() instead")]]
inline std::string to_yaml(const kistar_hand_ros2::msg::HandTarget & msg)
{
  return kistar_hand_ros2::msg::to_yaml(msg);
}

template<>
inline const char * data_type<kistar_hand_ros2::msg::HandTarget>()
{
  return "kistar_hand_ros2::msg::HandTarget";
}

template<>
inline const char * name<kistar_hand_ros2::msg::HandTarget>()
{
  return "kistar_hand_ros2/msg/HandTarget";
}

template<>
struct has_fixed_size<kistar_hand_ros2::msg::HandTarget>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<kistar_hand_ros2::msg::HandTarget>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<kistar_hand_ros2::msg::HandTarget>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__TRAITS_HPP_
