// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from kistar_hand_ros2:msg/FrankaArmTarget.idl
// generated code does not contain a copyright notice
#include "kistar_hand_ros2/msg/detail/franka_arm_target__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
kistar_hand_ros2__msg__FrankaArmTarget__init(kistar_hand_ros2__msg__FrankaArmTarget * msg)
{
  if (!msg) {
    return false;
  }
  // joint_targets
  // arm_id
  return true;
}

void
kistar_hand_ros2__msg__FrankaArmTarget__fini(kistar_hand_ros2__msg__FrankaArmTarget * msg)
{
  if (!msg) {
    return;
  }
  // joint_targets
  // arm_id
}

bool
kistar_hand_ros2__msg__FrankaArmTarget__are_equal(const kistar_hand_ros2__msg__FrankaArmTarget * lhs, const kistar_hand_ros2__msg__FrankaArmTarget * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // joint_targets
  for (size_t i = 0; i < 7; ++i) {
    if (lhs->joint_targets[i] != rhs->joint_targets[i]) {
      return false;
    }
  }
  // arm_id
  if (lhs->arm_id != rhs->arm_id) {
    return false;
  }
  return true;
}

bool
kistar_hand_ros2__msg__FrankaArmTarget__copy(
  const kistar_hand_ros2__msg__FrankaArmTarget * input,
  kistar_hand_ros2__msg__FrankaArmTarget * output)
{
  if (!input || !output) {
    return false;
  }
  // joint_targets
  for (size_t i = 0; i < 7; ++i) {
    output->joint_targets[i] = input->joint_targets[i];
  }
  // arm_id
  output->arm_id = input->arm_id;
  return true;
}

kistar_hand_ros2__msg__FrankaArmTarget *
kistar_hand_ros2__msg__FrankaArmTarget__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  kistar_hand_ros2__msg__FrankaArmTarget * msg = (kistar_hand_ros2__msg__FrankaArmTarget *)allocator.allocate(sizeof(kistar_hand_ros2__msg__FrankaArmTarget), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(kistar_hand_ros2__msg__FrankaArmTarget));
  bool success = kistar_hand_ros2__msg__FrankaArmTarget__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
kistar_hand_ros2__msg__FrankaArmTarget__destroy(kistar_hand_ros2__msg__FrankaArmTarget * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    kistar_hand_ros2__msg__FrankaArmTarget__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
kistar_hand_ros2__msg__FrankaArmTarget__Sequence__init(kistar_hand_ros2__msg__FrankaArmTarget__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  kistar_hand_ros2__msg__FrankaArmTarget * data = NULL;

  if (size) {
    data = (kistar_hand_ros2__msg__FrankaArmTarget *)allocator.zero_allocate(size, sizeof(kistar_hand_ros2__msg__FrankaArmTarget), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = kistar_hand_ros2__msg__FrankaArmTarget__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        kistar_hand_ros2__msg__FrankaArmTarget__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
kistar_hand_ros2__msg__FrankaArmTarget__Sequence__fini(kistar_hand_ros2__msg__FrankaArmTarget__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      kistar_hand_ros2__msg__FrankaArmTarget__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

kistar_hand_ros2__msg__FrankaArmTarget__Sequence *
kistar_hand_ros2__msg__FrankaArmTarget__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  kistar_hand_ros2__msg__FrankaArmTarget__Sequence * array = (kistar_hand_ros2__msg__FrankaArmTarget__Sequence *)allocator.allocate(sizeof(kistar_hand_ros2__msg__FrankaArmTarget__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = kistar_hand_ros2__msg__FrankaArmTarget__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
kistar_hand_ros2__msg__FrankaArmTarget__Sequence__destroy(kistar_hand_ros2__msg__FrankaArmTarget__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    kistar_hand_ros2__msg__FrankaArmTarget__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
kistar_hand_ros2__msg__FrankaArmTarget__Sequence__are_equal(const kistar_hand_ros2__msg__FrankaArmTarget__Sequence * lhs, const kistar_hand_ros2__msg__FrankaArmTarget__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!kistar_hand_ros2__msg__FrankaArmTarget__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
kistar_hand_ros2__msg__FrankaArmTarget__Sequence__copy(
  const kistar_hand_ros2__msg__FrankaArmTarget__Sequence * input,
  kistar_hand_ros2__msg__FrankaArmTarget__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(kistar_hand_ros2__msg__FrankaArmTarget);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    kistar_hand_ros2__msg__FrankaArmTarget * data =
      (kistar_hand_ros2__msg__FrankaArmTarget *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!kistar_hand_ros2__msg__FrankaArmTarget__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          kistar_hand_ros2__msg__FrankaArmTarget__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!kistar_hand_ros2__msg__FrankaArmTarget__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
