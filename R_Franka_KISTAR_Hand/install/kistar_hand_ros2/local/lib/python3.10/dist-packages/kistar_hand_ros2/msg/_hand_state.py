# generated from rosidl_generator_py/resource/_idl.py.em
# with input from kistar_hand_ros2:msg/HandState.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

# Member 'joint_positions'
# Member 'kinesthetic_sensors'
# Member 'tactile_sensors'
import numpy  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_HandState(type):
    """Metaclass of message 'HandState'."""

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
                'kistar_hand_ros2.msg.HandState')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__hand_state
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__hand_state
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__hand_state
            cls._TYPE_SUPPORT = module.type_support_msg__msg__hand_state
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__hand_state

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class HandState(metaclass=Metaclass_HandState):
    """Message class 'HandState'."""

    __slots__ = [
        '_joint_positions',
        '_kinesthetic_sensors',
        '_tactile_sensors',
        '_hand_id',
    ]

    _fields_and_field_types = {
        'joint_positions': 'int16[16]',
        'kinesthetic_sensors': 'int16[12]',
        'tactile_sensors': 'int16[60]',
        'hand_id': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('int16'), 16),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('int16'), 12),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('int16'), 60),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        if 'joint_positions' not in kwargs:
            self.joint_positions = numpy.zeros(16, dtype=numpy.int16)
        else:
            self.joint_positions = kwargs.get('joint_positions')
        if 'kinesthetic_sensors' not in kwargs:
            self.kinesthetic_sensors = numpy.zeros(12, dtype=numpy.int16)
        else:
            self.kinesthetic_sensors = kwargs.get('kinesthetic_sensors')
        if 'tactile_sensors' not in kwargs:
            self.tactile_sensors = numpy.zeros(60, dtype=numpy.int16)
        else:
            self.tactile_sensors = kwargs.get('tactile_sensors')
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
        if any(self.joint_positions != other.joint_positions):
            return False
        if any(self.kinesthetic_sensors != other.kinesthetic_sensors):
            return False
        if any(self.tactile_sensors != other.tactile_sensors):
            return False
        if self.hand_id != other.hand_id:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def joint_positions(self):
        """Message field 'joint_positions'."""
        return self._joint_positions

    @joint_positions.setter
    def joint_positions(self, value):
        if isinstance(value, numpy.ndarray):
            assert value.dtype == numpy.int16, \
                "The 'joint_positions' numpy.ndarray() must have the dtype of 'numpy.int16'"
            assert value.size == 16, \
                "The 'joint_positions' numpy.ndarray() must have a size of 16"
            self._joint_positions = value
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
                "The 'joint_positions' field must be a set or sequence with length 16 and each value of type 'int' and each integer in [-32768, 32767]"
        self._joint_positions = numpy.array(value, dtype=numpy.int16)

    @builtins.property
    def kinesthetic_sensors(self):
        """Message field 'kinesthetic_sensors'."""
        return self._kinesthetic_sensors

    @kinesthetic_sensors.setter
    def kinesthetic_sensors(self, value):
        if isinstance(value, numpy.ndarray):
            assert value.dtype == numpy.int16, \
                "The 'kinesthetic_sensors' numpy.ndarray() must have the dtype of 'numpy.int16'"
            assert value.size == 12, \
                "The 'kinesthetic_sensors' numpy.ndarray() must have a size of 12"
            self._kinesthetic_sensors = value
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
                 len(value) == 12 and
                 all(isinstance(v, int) for v in value) and
                 all(val >= -32768 and val < 32768 for val in value)), \
                "The 'kinesthetic_sensors' field must be a set or sequence with length 12 and each value of type 'int' and each integer in [-32768, 32767]"
        self._kinesthetic_sensors = numpy.array(value, dtype=numpy.int16)

    @builtins.property
    def tactile_sensors(self):
        """Message field 'tactile_sensors'."""
        return self._tactile_sensors

    @tactile_sensors.setter
    def tactile_sensors(self, value):
        if isinstance(value, numpy.ndarray):
            assert value.dtype == numpy.int16, \
                "The 'tactile_sensors' numpy.ndarray() must have the dtype of 'numpy.int16'"
            assert value.size == 60, \
                "The 'tactile_sensors' numpy.ndarray() must have a size of 60"
            self._tactile_sensors = value
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
                 len(value) == 60 and
                 all(isinstance(v, int) for v in value) and
                 all(val >= -32768 and val < 32768 for val in value)), \
                "The 'tactile_sensors' field must be a set or sequence with length 60 and each value of type 'int' and each integer in [-32768, 32767]"
        self._tactile_sensors = numpy.array(value, dtype=numpy.int16)

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
