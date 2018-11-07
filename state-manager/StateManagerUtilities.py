#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This file contains utility functions for testing, typechecks and formatting and conversions.
'''
import datetime
import select
import struct
import sys
import termios

FLOAT_TOLERANCE_REL = 5 * 1e-02
FLOAT_TOLERANCE_ABS = 1 * 1e-04
ZERO_TOLERANCE = 1 * 1e-04


def isClose(a, b, rel_tol=FLOAT_TOLERANCE_REL, abs_tol=FLOAT_TOLERANCE_ABS):
    """
    Test whether the float values a and b are approximately equal.
    :param a: First float value
    :param b: Second float value
    :param rel_tol: allowed relative tolerance (relative to bigger float value)
    :param abs_tol: allowed absolute tolerance
    :return: True if approximately equal under relative or absolute tolerance
    """
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def isZero(a):
    """
    Test whether float value a is zero.
    :param a: Float value
    :return: True if a is zero under tolerance of 1e-04 (ZERO_TOLERANCE)
    """
    return isClose(a, 0.0, 0.0, ZERO_TOLERANCE)


def typecheck(types, ranges=None):
    """
    Typecheck annotation utility for function
    :param types: Allowed types for values
    :param ranges: Allowed value ranges
    :return: True if types are allowed
    """

    def __f(f):
        def _f(*args, **kwargs):
            for a, t in zip(args, types):
                if not isinstance(a, t):
                    raise ValueError("Expected %s got %r" % (t, a))
            for a, r in zip(args, ranges or []):
                if r and not r[0] <= a <= r[1]:
                    raise ValueError("Should be in range %r: %r" % (r, a))
            return f(*args, **kwargs)

        return _f

    return __f


def formatTimestamp(timestamp, fileFormat=False):
    """
    Format the given timestamp to an human readable format

    :param timestamp: timestamp
    :param fileFormat: if True, different delimiter are used (usable for all filesystems)
    :return: Timestamp formatted
    """
    if timestamp is None:
        return None
    today = datetime.datetime.fromtimestamp(int(timestamp))
    if fileFormat:
        return today.strftime("%Y-%m-%d_%H-%M-%S")
    else:
        return today.strftime("%d.%m.%Y %H:%M:%S")


def normalize_value(value):
    """
    Normalize a Bro (as bitarray converted to int) value to an iec-104 normalized value
    :param value: Value to normalize
    :return: Normalized value
    """
    return value / 32768.0 if value / 32768.0 < 1 else (value / 32768.0) - 2


def doublefy_value(value):
    """
    Convert a Bro (as bitarray converted to int) value to a double value
    :param value: Value to convert
    :return: Converted value
    """
    return struct.unpack('f', struct.pack('I', value))[0]


class KeyPoller():
    # From https://stackoverflow.com/questions/13207678/whats-the-simplest-way-of-detecting-keyboard-input-in-python-from-the-terminal
    def __enter__(self):
        # Save the terminal settings
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)
        # New terminal setting unbuffered
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def poll(self):
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        if not dr == []:
            return sys.stdin.read(1)
        return None
