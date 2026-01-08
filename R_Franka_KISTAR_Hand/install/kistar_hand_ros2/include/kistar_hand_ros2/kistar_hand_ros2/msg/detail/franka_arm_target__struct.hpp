// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from kistar_hand_ros2:msg/FrankaArmTarget.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_TARGET__STRUCT_HPP_
#define KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_TARGET__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__kistar_hand_ros2__msg__FrankaArmTarget __attribute__((deprecated))
#else
# define DEPRECATED__kistar_hand_ros2__msg__FrankaArmTarget __declspec(deprecated)
#endif

namespace kistar_hand_ros2
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct FrankaArmTarget_
{
  using Type = FrankaArmTarget_<ContainerAllocator>;

  explicit FrankaArmTarget_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 7>::iterator, double>(this->joint_targets.begin(), this->joint_targets.end(), 0.0);
      this->arm_id = 0;
    }
  }

  explicit FrankaArmTarget_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : joint_targets(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 7>::iterator, double>(this->joint_targets.begin(), this->joint_targets.end(), 0.0);
      this->arm_id = 0;
    }
  }

  // field types and members
  using _joint_targets_type =
    std::array<double, 7>;
  _joint_targets_type joint_targets;
  using _arm_id_type =
    uint8_t;
  _arm_id_type arm_id;

  // setters for named parameter idiom
  Type & set__joint_targets(
    const std::array<double, 7> & _arg)
  {
    this->joint_targets = _arg;
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
    kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator> *;
  using ConstRawPtr =
    const kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__kistar_hand_ros2__msg__FrankaArmTarget
    std::shared_ptr<kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__kistar_hand_ros2__msg__FrankaArmTarget
    std::shared_ptr<kistar_hand_ros2::msg::FrankaArmTarget_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const FrankaArmTarget_ & other) const
  {
    if (this->joint_targets != other.joint_targets) {
      return false;
    }
    if (this->arm_id != other.arm_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const FrankaArmTarget_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct FrankaArmTarget_

// alias to use template instance with default allocator
using FrankaArmTarget =
  kistar_hand_ros2::msg::FrankaArmTarget_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace kistar_hand_ros2

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_TARGET__STRUCT_HPP_
