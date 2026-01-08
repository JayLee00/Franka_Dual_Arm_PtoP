// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from kistar_hand_ros2:msg/FrankaArmState.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_STATE__STRUCT_HPP_
#define KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_STATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__kistar_hand_ros2__msg__FrankaArmState __attribute__((deprecated))
#else
# define DEPRECATED__kistar_hand_ros2__msg__FrankaArmState __declspec(deprecated)
#endif

namespace kistar_hand_ros2
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct FrankaArmState_
{
  using Type = FrankaArmState_<ContainerAllocator>;

  explicit FrankaArmState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 7>::iterator, double>(this->joint_positions.begin(), this->joint_positions.end(), 0.0);
      std::fill<typename std::array<double, 7>::iterator, double>(this->joint_torques.begin(), this->joint_torques.end(), 0.0);
      this->arm_id = 0;
    }
  }

  explicit FrankaArmState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : joint_positions(_alloc),
    joint_torques(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 7>::iterator, double>(this->joint_positions.begin(), this->joint_positions.end(), 0.0);
      std::fill<typename std::array<double, 7>::iterator, double>(this->joint_torques.begin(), this->joint_torques.end(), 0.0);
      this->arm_id = 0;
    }
  }

  // field types and members
  using _joint_positions_type =
    std::array<double, 7>;
  _joint_positions_type joint_positions;
  using _joint_torques_type =
    std::array<double, 7>;
  _joint_torques_type joint_torques;
  using _arm_id_type =
    uint8_t;
  _arm_id_type arm_id;

  // setters for named parameter idiom
  Type & set__joint_positions(
    const std::array<double, 7> & _arg)
  {
    this->joint_positions = _arg;
    return *this;
  }
  Type & set__joint_torques(
    const std::array<double, 7> & _arg)
  {
    this->joint_torques = _arg;
    return *this;
  }
  Type & set__arm_id(
    const uint8_t & _arg)
  {
    this->arm_id = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator> *;
  using ConstRawPtr =
    const kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__kistar_hand_ros2__msg__FrankaArmState
    std::shared_ptr<kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__kistar_hand_ros2__msg__FrankaArmState
    std::shared_ptr<kistar_hand_ros2::msg::FrankaArmState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const FrankaArmState_ & other) const
  {
    if (this->joint_positions != other.joint_positions) {
      return false;
    }
    if (this->joint_torques != other.joint_torques) {
      return false;
    }
    if (this->arm_id != other.arm_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const FrankaArmState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct FrankaArmState_

// alias to use template instance with default allocator
using FrankaArmState =
  kistar_hand_ros2::msg::FrankaArmState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace kistar_hand_ros2

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_STATE__STRUCT_HPP_
