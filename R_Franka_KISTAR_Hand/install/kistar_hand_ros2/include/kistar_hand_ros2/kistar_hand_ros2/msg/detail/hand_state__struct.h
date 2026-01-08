// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from kistar_hand_ros2:msg/HandState.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__HAND_STATE__STRUCT_H_
#define KISTAR_HAND_ROS2__MSG__DETAIL__HAND_STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/HandState in the package kistar_hand_ros2.
/**
  * Hand 현재 상태 (shm -> ROS2)
  * Hand_Num = 2 (Left, Right)
  * Hand_DOF = 16
  * Kinesthetic_Sensor_DATA_NUM = 12 (4*3)
  * Tactile_Sensor_DATA_NUM = 60 (4*15)
 */
typedef struct kistar_hand_ros2__msg__HandState
{
  /// Hand_j_pos
  int16_t joint_positions[16];
  /// Hand_j_kin
  int16_t kinesthetic_sensors[12];
  /// Hand_j_tac
  int16_t tactile_sensors[60];
  /// 0=Right, 1=Left
  uint8_t hand_id;
} kistar_hand_ros2__msg__HandState;

// Struct for a sequence of kistar_hand_ros2__msg__HandState.
typedef struct kistar_hand_ros2__msg__HandState__Sequence
{
  kistar_hand_ros2__msg__HandState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} kistar_hand_ros2__msg__HandState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__HAND_STATE__STRUCT_H_
