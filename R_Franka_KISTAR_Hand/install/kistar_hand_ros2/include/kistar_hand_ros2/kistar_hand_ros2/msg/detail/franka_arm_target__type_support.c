// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from kistar_hand_ros2:msg/FrankaArmTarget.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "kistar_hand_ros2/msg/detail/franka_arm_target__rosidl_typesupport_introspection_c.h"
#include "kistar_hand_ros2/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "kistar_hand_ros2/msg/detail/franka_arm_target__functions.h"
#include "kistar_hand_ros2/msg/detail/franka_arm_target__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  kistar_hand_ros2__msg__FrankaArmTarget__init(message_memory);
}

void kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_fini_function(void * message_memory)
{
  kistar_hand_ros2__msg__FrankaArmTarget__fini(message_memory);
}

size_t kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__size_function__FrankaArmTarget__joint_targets(
  const void * untyped_member)
{
  (void)untyped_member;
  return 7;
}

const void * kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__get_const_function__FrankaArmTarget__joint_targets(
  const void * untyped_member, size_t index)
{
  const double * member =
    (const double *)(untyped_member);
  return &member[index];
}

void * kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__get_function__FrankaArmTarget__joint_targets(
  void * untyped_member, size_t index)
{
  double * member =
    (double *)(untyped_member);
  return &member[index];
}

void kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__fetch_function__FrankaArmTarget__joint_targets(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__get_const_function__FrankaArmTarget__joint_targets(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__assign_function__FrankaArmTarget__joint_targets(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__get_function__FrankaArmTarget__joint_targets(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

static rosidl_typesupport_introspection_c__MessageMember kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_message_member_array[2] = {
  {
    "joint_targets",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    7,  // array size
    false,  // is upper bound
    offsetof(kistar_hand_ros2__msg__FrankaArmTarget, joint_targets),  // bytes offset in struct
    NULL,  // default value
    kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__size_function__FrankaArmTarget__joint_targets,  // size() function pointer
    kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__get_const_function__FrankaArmTarget__joint_targets,  // get_const(index) function pointer
    kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__get_function__FrankaArmTarget__joint_targets,  // get(index) function pointer
    kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__fetch_function__FrankaArmTarget__joint_targets,  // fetch(index, &value) function pointer
    kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__assign_function__FrankaArmTarget__joint_targets,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "arm_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(kistar_hand_ros2__msg__FrankaArmTarget, arm_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_message_members = {
  "kistar_hand_ros2__msg",  // message namespace
  "FrankaArmTarget",  // message name
  2,  // number of fields
  sizeof(kistar_hand_ros2__msg__FrankaArmTarget),
  kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_message_member_array,  // message members
  kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_init_function,  // function to initialize message memory (memory has to be allocated)
  kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_message_type_support_handle = {
  0,
  &kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_kistar_hand_ros2
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, kistar_hand_ros2, msg, FrankaArmTarget)() {
  if (!kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_message_type_support_handle.typesupport_identifier) {
    kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &kistar_hand_ros2__msg__FrankaArmTarget__rosidl_typesupport_introspection_c__FrankaArmTarget_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
