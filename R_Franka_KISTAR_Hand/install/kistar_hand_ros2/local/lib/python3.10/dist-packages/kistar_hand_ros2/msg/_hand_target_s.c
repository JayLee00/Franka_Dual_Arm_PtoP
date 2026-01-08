// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from kistar_hand_ros2:msg/HandTarget.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "kistar_hand_ros2/msg/detail/hand_target__struct.h"
#include "kistar_hand_ros2/msg/detail/hand_target__functions.h"

#include "rosidl_runtime_c/primitives_sequence.h"
#include "rosidl_runtime_c/primitives_sequence_functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool kistar_hand_ros2__msg__hand_target__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[45];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("kistar_hand_ros2.msg._hand_target.HandTarget", full_classname_dest, 44) == 0);
  }
  kistar_hand_ros2__msg__HandTarget * ros_message = _ros_message;
  {  // joint_targets
    PyObject * field = PyObject_GetAttrString(_pymsg, "joint_targets");
    if (!field) {
      return false;
    }
    {
      // TODO(dirk-thomas) use a better way to check the type before casting
      assert(field->ob_type != NULL);
      assert(field->ob_type->tp_name != NULL);
      assert(strcmp(field->ob_type->tp_name, "numpy.ndarray") == 0);
      PyArrayObject * seq_field = (PyArrayObject *)field;
      Py_INCREF(seq_field);
      assert(PyArray_NDIM(seq_field) == 1);
      assert(PyArray_TYPE(seq_field) == NPY_INT16);
      Py_ssize_t size = 16;
      int16_t * dest = ros_message->joint_targets;
      for (Py_ssize_t i = 0; i < size; ++i) {
        int16_t tmp = *(npy_int16 *)PyArray_GETPTR1(seq_field, i);
        memcpy(&dest[i], &tmp, sizeof(int16_t));
      }
      Py_DECREF(seq_field);
    }
    Py_DECREF(field);
  }
  {  // movement_duration
    PyObject * field = PyObject_GetAttrString(_pymsg, "movement_duration");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->movement_duration = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // hand_id
    PyObject * field = PyObject_GetAttrString(_pymsg, "hand_id");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->hand_id = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * kistar_hand_ros2__msg__hand_target__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of HandTarget */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("kistar_hand_ros2.msg._hand_target");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "HandTarget");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  kistar_hand_ros2__msg__HandTarget * ros_message = (kistar_hand_ros2__msg__HandTarget *)raw_ros_message;
  {  // joint_targets
    PyObject * field = NULL;
    field = PyObject_GetAttrString(_pymessage, "joint_targets");
    if (!field) {
      return NULL;
    }
    assert(field->ob_type != NULL);
    assert(field->ob_type->tp_name != NULL);
    assert(strcmp(field->ob_type->tp_name, "numpy.ndarray") == 0);
    PyArrayObject * seq_field = (PyArrayObject *)field;
    assert(PyArray_NDIM(seq_field) == 1);
    assert(PyArray_TYPE(seq_field) == NPY_INT16);
    assert(sizeof(npy_int16) == sizeof(int16_t));
    npy_int16 * dst = (npy_int16 *)PyArray_GETPTR1(seq_field, 0);
    int16_t * src = &(ros_message->joint_targets[0]);
    memcpy(dst, src, 16 * sizeof(int16_t));
    Py_DECREF(field);
  }
  {  // movement_duration
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->movement_duration);
    {
      int rc = PyObject_SetAttrString(_pymessage, "movement_duration", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // hand_id
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->hand_id);
    {
      int rc = PyObject_SetAttrString(_pymessage, "hand_id", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
