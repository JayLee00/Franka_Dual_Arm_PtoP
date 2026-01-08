// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from kistar_hand_ros2:msg/HandState.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__HAND_STATE__STRUCT_HPP_
#define KISTAR_HAND_ROS2__MSG__DETAIL__HAND_STATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__kistar_hand_ros2__msg__HandState __attribute__((deprecated))
#else
# define DEPRECATED__kistar_hand_ros2__msg__HandState __declspec(deprecated)
#endif

namespace kistar_hand_ros2
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct HandState_
{
  using Type = HandState_<ContainerAllocator>;

  explicit HandState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<int16_t, 16>::iterator, int16_t>(this->joint_positions.begin(), this->joint_positions.end(), 0);
      std::fill<typename std::array<int16_t, 12>::iterator, int16_t>(this->kinesthetic_sensors.begin(), this->kinesthetic_sensors.end(), 0);
      std::fill<typename std::array<int16_t, 60>::iterator, int16_t>(this->tactile_sensors.begin(), this->tactile_sensors.end(), 0);
      this->hand_id = 0;
    }
  }

  explicit HandState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : joint_positions(_alloc),
    kinesthetic_sensors(_alloc),
    tactile_sensors(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<int16_t, 16>::iterator, int16_t>(this->joint_positions.begin(), this->joint_positions.end(), 0);
      std::fill<typename std::array<int16_t, 12>::iterator, int16_t>(this->kinesthetic_sensors.begin(), this->kinesthetic_sensors.end(), 0);
      std::fill<typename std::array<int16_t, 60>::iterator, int16_t>(this->tactile_sensors.begin(), this->tactile_sensors.end(), 0);
      this->hand_id = 0;
    }
  }

  // field types and members
  using _joint_positions_type =
    std::array<int16_t, 16>;
  _joint_positions_type joint_positions;
  using _kinesthetic_sensors_type =
    std::array<int16_t, 12>;
  _kinesthetic_sensors_type kinesthetic_sensors;
  using _tactile_sensors_type =
    std::array<int16_t, 60>;
  _tactile_sensors_type tactile_sensors;
  using _hand_id_type =
    uint8_t;
  _hand_id_type hand_id;

  // setters for named parameter idiom
  Type & set__joint_positions(
    const std::array<int16_t, 16> & _arg)
  {
    this->joint_positions = _arg;
    return *this;
  }
  Type & set__kinesthetic_sensors(
    const std::array<int16_t, 12> & _arg)
  {
    this->kinesthetic_sensors = _arg;
    return *this;
  }
  Type & set__tactile_sensors(
    const std::array<int16_t, 60> & _arg)
  {
    this->tactile_sensors = _arg;
    return *this;
  }
  Type & set__hand_id(
    const uint8_t & _arg)
  {
    this->hand_id = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    kistar_hand_ros2::msg::HandState_<ContainerAllocator> *;
  using ConstRawPtr =
    const kistar_hand_ros2::msg::HandState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<kistar_hand_ros2::msg::HandState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<kistar_hand_ros2::msg::HandState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      kistar_hand_ros2::msg::HandState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<kistar_hand_ros2::msg::HandState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      kistar_hand_ros2::msg::HandState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<kistar_hand_ros2::msg::HandState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<kistar_hand_ros2::msg::HandState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<kistar_hand_ros2::msg::HandState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__kistar_hand_ros2__msg__HandState
    std::shared_ptr<kistar_hand_ros2::msg::HandState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__kistar_hand_ros2__msg__HandState
    std::shared_ptr<kistar_hand_ros2::msg::HandState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const HandState_ & other) const
  {
    if (this->joint_positions != other.joint_positions) {
      return false;
    }
    if (this->kinesthetic_sensors != other.kinesthetic_sensors) {
      return false;
    }
    if (this->tactile_sensors != other.tactile_sensors) {
      return false;
    }
    if (this->hand_id != other.hand_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const HandState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct HandState_

// alias to use template instance with default allocator
using HandState =
  kistar_hand_ros2::msg::HandState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace kistar_hand_ros2

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__HAND_STATE__STRUCT_HPP_
