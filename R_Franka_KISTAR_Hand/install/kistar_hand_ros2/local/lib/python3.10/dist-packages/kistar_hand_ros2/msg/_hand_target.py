# generated from rosidl_generator_py/resource/_idl.py.em
# with input from kistar_hand_ros2:msg/HandTarget.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

# Member 'joint_targets'
import numpy  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_HandTarget(type):
    """Metaclass of message 'HandTarget'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('kistar_hand_ros2')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'kistar_hand_ros2.msg.HandTarget')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__hand_target
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__hand_target
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__hand_target
            cls._TYPE_SUPPORT = module.type_support_msg__msg__hand_target
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__hand_target

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class HandTarget(metaclass=Metaclass_HandTarget):
    """Message class 'HandTarget'."""

    __slots__ = [
        '_joint_targets',
        '_movement_duration',
        '_hand_id',
    ]

    _fields_and_field_types = {
        'joint_targets': 'int16[16]',
        'movement_duration': 'double',
        'hand_id': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('int16'), 16),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        if 'joint_targets' not in kwargs:
            self.joint_targets = numpy.zeros(16, dtype=numpy.int16)
        else:
            self.joint_targets = kwargs.get('joint_targets')
        self.movement_duration = kwargs.get('movement_duration', float())
        self.hand_id = kwargs.get('hand_id', int())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if any(self.joint_targets != other.joint_targets):
            return False
        if self.movement_duration != other.movement_duration:
            return False
        if self.hand_id != other.hand_id:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def joint_targets(self):
        """Message field 'joint_targets'."""
        return self._joint_targets

    @joint_targets.setter
    def joint_targets(self, value):
        if isinstance(value, numpy.ndarray):
            assert value.dtype == numpy.int16, \
                "The 'joint_targets' numpy.ndarray() must have the dtype of 'numpy.int16'"
            assert value.size == 16, \
                "The 'joint_targets' numpy.ndarray() must have a size of 16"
            self._joint_targets = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 len(value) == 16 and
                 all(isinstance(v, int) for v in value) and
                 all(val >= -32768 and val < 32768 for val in value)), \
                "The 'joint_targets' field must be a set or sequence with length 16 and each value of type 'int' and each integer in [-32768, 32767]"
        self._joint_targets = numpy.array(value, dtype=numpy.int16)

    @builtins.property
    def movement_duration(self):
        """Message field 'movement_duration'."""
        return self._movement_duration

    @movement_duration.setter
    def movement_duration(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'movement_duration' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'movement_duration' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._movement_duration = value

    @builtins.property
    def hand_id(self):
        """Message field 'hand_id'."""
        return self._hand_id

    @hand_id.setter
    def hand_id(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'hand_id' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'hand_id' field must be an unsigned integer in [0, 255]"
        self._hand_id = value
