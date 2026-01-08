// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from kistar_hand_ros2:msg/FrankaArmState.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_STATE__TRAITS_HPP_
#define KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_STATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "kistar_hand_ros2/msg/detail/franka_arm_state__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace kistar_hand_ros2
{

namespace msg
{

inline void to_flow_style_yaml(
  const FrankaArmState & msg,
  std::ostream & out)
{
  out << "{";
  // member: joint_positions
  {
    if (msg.joint_positions.size() == 0) {
      out << "joint_positions: []";
    } else {
      out << "joint_positions: [";
      size_t pending_items = msg.joint_positions.size();
      for (auto item : msg.joint_positions) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: joint_torques
  {
    if (msg.joint_torques.size() == 0) {
      out << "joint_torques: []";
    } else {
      out << "joint_torques: [";
      size_t pending_items = msg.joint_torques.size();
      for (auto item : msg.joint_torques) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: arm_id
  {
    out << "arm_id: ";
    rosidl_generator_traits::value_to_yaml(msg.arm_id, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const FrankaArmState & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: joint_positions
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.joint_positions.size() == 0) {
      out << "joint_positions: []\n";
    } else {
      out << "joint_positions:\n";
      for (auto item : msg.joint_positions) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: joint_torques
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.joint_torques.size() == 0) {
      out << "joint_torques: []\n";
    } else {
      out << "joint_torques:\n";
      for (auto item : msg.joint_torques) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: arm_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "arm_id: ";
    rosidl_generator_traits::value_to_yaml(msg.arm_id, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const FrankaArmState & msg, bool use_flow_style = false)
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
  const kistar_hand_ros2::msg::FrankaArmState & msg,
  std::ostream & out, size_t indentation = 0)
{
  kistar_hand_ros2::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use kistar_hand_ros2::msg::to_yaml() instead")]]
inline std::string to_yaml(const kistar_hand_ros2::msg::FrankaArmState & msg)
{
  return kistar_hand_ros2::msg::to_yaml(msg);
}

template<>
inline const char * data_type<kistar_hand_ros2::msg::FrankaArmState>()
{
  return "kistar_hand_ros2::msg::FrankaArmState";
}

template<>
inline const char * name<kistar_hand_ros2::msg::FrankaArmState>()
{
  return "kistar_hand_ros2/msg/FrankaArmState";
}

template<>
struct has_fixed_size<kistar_hand_ros2::msg::FrankaArmState>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<kistar_hand_ros2::msg::FrankaArmState>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<kistar_hand_ros2::msg::FrankaArmState>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_STATE__TRAITS_HPP_
