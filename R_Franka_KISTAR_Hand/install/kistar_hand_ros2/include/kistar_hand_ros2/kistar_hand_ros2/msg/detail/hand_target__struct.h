// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from kistar_hand_ros2:msg/HandTarget.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__STRUCT_H_
#define KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/HandTarget in the package kistar_hand_ros2.
/**
  * Hand 목표 (ROS2 -> shm)
  * Hand_Num = 2 (Left, Right)
  * Hand_DOF = 16
 */
typedef struct kistar_hand_ros2__msg__HandTarget
{
  /// Hand_j_tar
  int16_t joint_targets[16];
  /// hand_movement_duration
  double movement_duration;
  /// 0=Right, 1=Left
  uint8_t hand_id;
} kistar_hand_ros2__msg__HandTarget;

// Struct for a sequence of kistar_hand_ros2__msg__HandTarget.
typedef struct kistar_hand_ros2__msg__HandTarget__Sequence
{
  kistar_hand_ros2__msg__HandTarget * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} kistar_hand_ros2__msg__HandTarget__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__STRUCT_H_
