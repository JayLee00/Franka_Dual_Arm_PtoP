// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from kistar_hand_ros2:msg/FrankaArmState.idl
// generated code does not contain a copyright notice
#include "kistar_hand_ros2/msg/detail/franka_arm_state__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
kistar_hand_ros2__msg__FrankaArmState__init(kistar_hand_ros2__msg__FrankaArmState * msg)
{
  if (!msg) {
    return false;
  }
  // joint_positions
  // joint_torques
  // arm_id
  return true;
}

void
kistar_hand_ros2__msg__FrankaArmState__fini(kistar_hand_ros2__msg__FrankaArmState * msg)
{
  if (!msg) {
    return;
  }
  // joint_positions
  // joint_torques
  // arm_id
}

bool
kistar_hand_ros2__msg__FrankaArmState__are_equal(const kistar_hand_ros2__msg__FrankaArmState * lhs, const kistar_hand_ros2__msg__FrankaArmState * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // joint_positions
  for (size_t i = 0; i < 7; ++i) {
    if (lhs->joint_positions[i] != rhs->joint_positions[i]) {
      return false;
    }
  }
  // joint_torques
  for (size_t i = 0; i < 7; ++i) {
    if (lhs->joint_torques[i] != rhs->joint_torques[i]) {
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
kistar_hand_ros2__msg__FrankaArmState__copy(
  const kistar_hand_ros2__msg__FrankaArmState * input,
  kistar_hand_ros2__msg__FrankaArmState * output)
{
  if (!input || !output) {
    return false;
  }
  // joint_positions
  for (size_t i = 0; i < 7; ++i) {
    output->joint_positions[i] = input->joint_positions[i];
  }
  // joint_torques
  for (size_t i = 0; i < 7; ++i) {
    output->joint_torques[i] = input->joint_torques[i];
  }
  // arm_id
  output->arm_id = input->arm_id;
  return true;
}

kistar_hand_ros2__msg__FrankaArmState *
kistar_hand_ros2__msg__FrankaArmState__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  kistar_hand_ros2__msg__FrankaArmState * msg = (kistar_hand_ros2__msg__FrankaArmState *)allocator.allocate(sizeof(kistar_hand_ros2__msg__FrankaArmState), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(kistar_hand_ros2__msg__FrankaArmState));
  bool success = kistar_hand_ros2__msg__FrankaArmState__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
kistar_hand_ros2__msg__FrankaArmState__destroy(kistar_hand_ros2__msg__FrankaArmState * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    kistar_hand_ros2__msg__FrankaArmState__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
kistar_hand_ros2__msg__FrankaArmState__Sequence__init(kistar_hand_ros2__msg__FrankaArmState__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  kistar_hand_ros2__msg__FrankaArmState * data = NULL;

  if (size) {
    data = (kistar_hand_ros2__msg__FrankaArmState *)allocator.zero_allocate(size, sizeof(kistar_hand_ros2__msg__FrankaArmState), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = kistar_hand_ros2__msg__FrankaArmState__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        kistar_hand_ros2__msg__FrankaArmState__fini(&data[i - 1]);
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
kistar_hand_ros2__msg__FrankaArmState__Sequence__fini(kistar_hand_ros2__msg__FrankaArmState__Sequence * array)
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
      kistar_hand_ros2__msg__FrankaArmState__fini(&array->data[i]);
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

kistar_hand_ros2__msg__FrankaArmState__Sequence *
kistar_hand_ros2__msg__FrankaArmState__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  kistar_hand_ros2__msg__FrankaArmState__Sequence * array = (kistar_hand_ros2__msg__FrankaArmState__Sequence *)allocator.allocate(sizeof(kistar_hand_ros2__msg__FrankaArmState__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = kistar_hand_ros2__msg__FrankaArmState__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
kistar_hand_ros2__msg__FrankaArmState__Sequence__destroy(kistar_hand_ros2__msg__FrankaArmState__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    kistar_hand_ros2__msg__FrankaArmState__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
kistar_hand_ros2__msg__FrankaArmState__Sequence__are_equal(const kistar_hand_ros2__msg__FrankaArmState__Sequence * lhs, const kistar_hand_ros2__msg__FrankaArmState__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!kistar_hand_ros2__msg__FrankaArmState__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
kistar_hand_ros2__msg__FrankaArmState__Sequence__copy(
  const kistar_hand_ros2__msg__FrankaArmState__Sequence * input,
  kistar_hand_ros2__msg__FrankaArmState__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(kistar_hand_ros2__msg__FrankaArmState);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    kistar_hand_ros2__msg__FrankaArmState * data =
      (kistar_hand_ros2__msg__FrankaArmState *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!kistar_hand_ros2__msg__FrankaArmState__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          kistar_hand_ros2__msg__FrankaArmState__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!kistar_hand_ros2__msg__FrankaArmState__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
