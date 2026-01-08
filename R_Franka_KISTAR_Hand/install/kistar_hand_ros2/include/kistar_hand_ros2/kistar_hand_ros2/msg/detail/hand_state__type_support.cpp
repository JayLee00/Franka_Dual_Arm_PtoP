// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from kistar_hand_ros2:msg/HandState.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "kistar_hand_ros2/msg/detail/hand_state__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace kistar_hand_ros2
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void HandState_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) kistar_hand_ros2::msg::HandState(_init);
}

void HandState_fini_function(void * message_memory)
{
  auto typed_message = static_cast<kistar_hand_ros2::msg::HandState *>(message_memory);
  typed_message->~HandState();
}

size_t size_function__HandState__joint_positions(const void * untyped_member)
{
  (void)untyped_member;
  return 16;
}

const void * get_const_function__HandState__joint_positions(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<int16_t, 16> *>(untyped_member);
  return &member[index];
}

void * get_function__HandState__joint_positions(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<int16_t, 16> *>(untyped_member);
  return &member[index];
}

void fetch_function__HandState__joint_positions(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int16_t *>(
    get_const_function__HandState__joint_positions(untyped_member, index));
  auto & value = *reinterpret_cast<int16_t *>(untyped_value);
  value = item;
}

void assign_function__HandState__joint_positions(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int16_t *>(
    get_function__HandState__joint_positions(untyped_member, index));
  const auto & value = *reinterpret_cast<const int16_t *>(untyped_value);
  item = value;
}

size_t size_function__HandState__kinesthetic_sensors(const void * untyped_member)
{
  (void)untyped_member;
  return 12;
}

const void * get_const_function__HandState__kinesthetic_sensors(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<int16_t, 12> *>(untyped_member);
  return &member[index];
}

void * get_function__HandState__kinesthetic_sensors(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<int16_t, 12> *>(untyped_member);
  return &member[index];
}

void fetch_function__HandState__kinesthetic_sensors(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int16_t *>(
    get_const_function__HandState__kinesthetic_sensors(untyped_member, index));
  auto & value = *reinterpret_cast<int16_t *>(untyped_value);
  value = item;
}

void assign_function__HandState__kinesthetic_sensors(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int16_t *>(
    get_function__HandState__kinesthetic_sensors(untyped_member, index));
  const auto & value = *reinterpret_cast<const int16_t *>(untyped_value);
  item = value;
}

size_t size_function__HandState__tactile_sensors(const void * untyped_member)
{
  (void)untyped_member;
  return 60;
}

const void * get_const_function__HandState__tactile_sensors(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<int16_t, 60> *>(untyped_member);
  return &member[index];
}

void * get_function__HandState__tactile_sensors(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<int16_t, 60> *>(untyped_member);
  return &member[index];
}

void fetch_function__HandState__tactile_sensors(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int16_t *>(
    get_const_function__HandState__tactile_sensors(untyped_member, index));
  auto & value = *reinterpret_cast<int16_t *>(untyped_value);
  value = item;
}

void assign_function__HandState__tactile_sensors(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int16_t *>(
    get_function__HandState__tactile_sensors(untyped_member, index));
  const auto & value = *reinterpret_cast<const int16_t *>(untyped_value);
  item = value;
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember HandState_message_member_array[4] = {
  {
    "joint_positions",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT16,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    16,  // array size
    false,  // is upper bound
    offsetof(kistar_hand_ros2::msg::HandState, joint_positions),  // bytes offset in struct
    nullptr,  // default value
    size_function__HandState__joint_positions,  // size() function pointer
    get_const_function__HandState__joint_positions,  // get_const(index) function pointer
    get_function__HandState__joint_positions,  // get(index) function pointer
    fetch_function__HandState__joint_positions,  // fetch(index, &value) function pointer
    assign_function__HandState__joint_positions,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "kinesthetic_sensors",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT16,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    12,  // array size
    false,  // is upper bound
    offsetof(kistar_hand_ros2::msg::HandState, kinesthetic_sensors),  // bytes offset in struct
    nullptr,  // default value
    size_function__HandState__kinesthetic_sensors,  // size() function pointer
    get_const_function__HandState__kinesthetic_sensors,  // get_const(index) function pointer
    get_function__HandState__kinesthetic_sensors,  // get(index) function pointer
    fetch_function__HandState__kinesthetic_sensors,  // fetch(index, &value) function pointer
    assign_function__HandState__kinesthetic_sensors,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "tactile_sensors",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT16,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    60,  // array size
    false,  // is upper bound
    offsetof(kistar_hand_ros2::msg::HandState, tactile_sensors),  // bytes offset in struct
    nullptr,  // default value
    size_function__HandState__tactile_sensors,  // size() function pointer
    get_const_function__HandState__tactile_sensors,  // get_const(index) function pointer
    get_function__HandState__tactile_sensors,  // get(index) function pointer
    fetch_function__HandState__tactile_sensors,  // fetch(index, &value) function pointer
    assign_function__HandState__tactile_sensors,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "hand_id",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(kistar_hand_ros2::msg::HandState, hand_id),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers HandState_message_members = {
  "kistar_hand_ros2::msg",  // message namespace
  "HandState",  // message name
  4,  // number of fields
  sizeof(kistar_hand_ros2::msg::HandState),
  HandState_message_member_array,  // message members
  HandState_init_function,  // function to initialize message memory (memory has to be allocated)
  HandState_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t HandState_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &HandState_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace kistar_hand_ros2


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<kistar_hand_ros2::msg::HandState>()
{
  return &::kistar_hand_ros2::msg::rosidl_typesupport_introspection_cpp::HandState_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, kistar_hand_ros2, msg, HandState)() {
  return &::kistar_hand_ros2::msg::rosidl_typesupport_introspection_cpp::HandState_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
