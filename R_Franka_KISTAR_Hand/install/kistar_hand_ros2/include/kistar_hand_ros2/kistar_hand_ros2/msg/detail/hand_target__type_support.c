// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from kistar_hand_ros2:msg/HandTarget.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "kistar_hand_ros2/msg/detail/hand_target__rosidl_typesupport_introspection_c.h"
#include "kistar_hand_ros2/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "kistar_hand_ros2/msg/detail/hand_target__functions.h"
#include "kistar_hand_ros2/msg/detail/hand_target__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  kistar_hand_ros2__msg__HandTarget__init(message_memory);
}

void kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_fini_function(void * message_memory)
{
  kistar_hand_ros2__msg__HandTarget__fini(message_memory);
}

size_t kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__size_function__HandTarget__joint_targets(
  const void * untyped_member)
{
  (void)untyped_member;
  return 16;
}

const void * kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__get_const_function__HandTarget__joint_targets(
  const void * untyped_member, size_t index)
{
  const int16_t * member =
    (const int16_t *)(untyped_member);
  return &member[index];
}

void * kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__get_function__HandTarget__joint_targets(
  void * untyped_member, size_t index)
{
  int16_t * member =
    (int16_t *)(untyped_member);
  return &member[index];
}

void kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__fetch_function__HandTarget__joint_targets(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int16_t * item =
    ((const int16_t *)
    kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__get_const_function__HandTarget__joint_targets(untyped_member, index));
  int16_t * value =
    (int16_t *)(untyped_value);
  *value = *item;
}

void kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__assign_function__HandTarget__joint_targets(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int16_t * item =
    ((int16_t *)
    kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__get_function__HandTarget__joint_targets(untyped_member, index));
  const int16_t * value =
    (const int16_t *)(untyped_value);
  *item = *value;
}

static rosidl_typesupport_introspection_c__MessageMember kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_message_member_array[3] = {
  {
    "joint_targets",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT16,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    16,  // array size
    false,  // is upper bound
    offsetof(kistar_hand_ros2__msg__HandTarget, joint_targets),  // bytes offset in struct
    NULL,  // default value
    kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__size_function__HandTarget__joint_targets,  // size() function pointer
    kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__get_const_function__HandTarget__joint_targets,  // get_const(index) function pointer
    kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__get_function__HandTarget__joint_targets,  // get(index) function pointer
    kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__fetch_function__HandTarget__joint_targets,  // fetch(index, &value) function pointer
    kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__assign_function__HandTarget__joint_targets,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "movement_duration",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(kistar_hand_ros2__msg__HandTarget, movement_duration),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "hand_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(kistar_hand_ros2__msg__HandTarget, hand_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_message_members = {
  "kistar_hand_ros2__msg",  // message namespace
  "HandTarget",  // message name
  3,  // number of fields
  sizeof(kistar_hand_ros2__msg__HandTarget),
  kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_message_member_array,  // message members
  kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_init_function,  // function to initialize message memory (memory has to be allocated)
  kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_message_type_support_handle = {
  0,
  &kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_kistar_hand_ros2
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, kistar_hand_ros2, msg, HandTarget)() {
  if (!kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_message_type_support_handle.typesupport_identifier) {
    kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &kistar_hand_ros2__msg__HandTarget__rosidl_typesupport_introspection_c__HandTarget_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
