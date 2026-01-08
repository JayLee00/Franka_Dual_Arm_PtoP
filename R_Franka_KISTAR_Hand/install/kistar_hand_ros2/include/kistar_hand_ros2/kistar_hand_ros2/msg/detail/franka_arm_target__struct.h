// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from kistar_hand_ros2:msg/FrankaArmTarget.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_TARGET__STRUCT_H_
#define KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_TARGET__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/FrankaArmTarget in the package kistar_hand_ros2.
/**
  * Franka Arm 목표 (ROS2 -> shm)
  * Arm_Num = 2 (Left, Right)
  * Arm_DOF = 7
 */
typedef struct kistar_hand_ros2__msg__FrankaArmTarget
{
  /// Arm_j_tar
  double joint_targets[7];
  /// 0=Right, 1=Left
  uint8_t arm_id;
} kistar_hand_ros2__msg__FrankaArmTarget;

// Struct for a sequence of kistar_hand_ros2__msg__FrankaArmTarget.
typedef struct kistar_hand_ros2__msg__FrankaArmTarget__Sequence
{
  kistar_hand_ros2__msg__FrankaArmTarget * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} kistar_hand_ros2__msg__FrankaArmTarget__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__FRANKA_ARM_TARGET__STRUCT_H_
