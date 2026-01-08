// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from kistar_hand_ros2:msg/HandTarget.idl
// generated code does not contain a copyright notice

#ifndef KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__FUNCTIONS_H_
#define KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "kistar_hand_ros2/msg/rosidl_generator_c__visibility_control.h"

#include "kistar_hand_ros2/msg/detail/hand_target__struct.h"

/// Initialize msg/HandTarget message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * kistar_hand_ros2__msg__HandTarget
 * )) before or use
 * kistar_hand_ros2__msg__HandTarget__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
bool
kistar_hand_ros2__msg__HandTarget__init(kistar_hand_ros2__msg__HandTarget * msg);

/// Finalize msg/HandTarget message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
void
kistar_hand_ros2__msg__HandTarget__fini(kistar_hand_ros2__msg__HandTarget * msg);

/// Create msg/HandTarget message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * kistar_hand_ros2__msg__HandTarget__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
kistar_hand_ros2__msg__HandTarget *
kistar_hand_ros2__msg__HandTarget__create();

/// Destroy msg/HandTarget message.
/**
 * It calls
 * kistar_hand_ros2__msg__HandTarget__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
void
kistar_hand_ros2__msg__HandTarget__destroy(kistar_hand_ros2__msg__HandTarget * msg);

/// Check for msg/HandTarget message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
bool
kistar_hand_ros2__msg__HandTarget__are_equal(const kistar_hand_ros2__msg__HandTarget * lhs, const kistar_hand_ros2__msg__HandTarget * rhs);

/// Copy a msg/HandTarget message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
bool
kistar_hand_ros2__msg__HandTarget__copy(
  const kistar_hand_ros2__msg__HandTarget * input,
  kistar_hand_ros2__msg__HandTarget * output);

/// Initialize array of msg/HandTarget messages.
/**
 * It allocates the memory for the number of elements and calls
 * kistar_hand_ros2__msg__HandTarget__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
bool
kistar_hand_ros2__msg__HandTarget__Sequence__init(kistar_hand_ros2__msg__HandTarget__Sequence * array, size_t size);

/// Finalize array of msg/HandTarget messages.
/**
 * It calls
 * kistar_hand_ros2__msg__HandTarget__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
void
kistar_hand_ros2__msg__HandTarget__Sequence__fini(kistar_hand_ros2__msg__HandTarget__Sequence * array);

/// Create array of msg/HandTarget messages.
/**
 * It allocates the memory for the array and calls
 * kistar_hand_ros2__msg__HandTarget__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
kistar_hand_ros2__msg__HandTarget__Sequence *
kistar_hand_ros2__msg__HandTarget__Sequence__create(size_t size);

/// Destroy array of msg/HandTarget messages.
/**
 * It calls
 * kistar_hand_ros2__msg__HandTarget__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
void
kistar_hand_ros2__msg__HandTarget__Sequence__destroy(kistar_hand_ros2__msg__HandTarget__Sequence * array);

/// Check for msg/HandTarget message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
bool
kistar_hand_ros2__msg__HandTarget__Sequence__are_equal(const kistar_hand_ros2__msg__HandTarget__Sequence * lhs, const kistar_hand_ros2__msg__HandTarget__Sequence * rhs);

/// Copy an array of msg/HandTarget messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_kistar_hand_ros2
bool
kistar_hand_ros2__msg__HandTarget__Sequence__copy(
  const kistar_hand_ros2__msg__HandTarget__Sequence * input,
  kistar_hand_ros2__msg__HandTarget__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // KISTAR_HAND_ROS2__MSG__DETAIL__HAND_TARGET__FUNCTIONS_H_
