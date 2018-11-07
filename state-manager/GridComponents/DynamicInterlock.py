#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents an dynamic interlock.
'''
from GridComponents.AbstractInterlock import AbstractInterlock


class DynamicInterlock(AbstractInterlock):
    def __init__(self, name, interlockedSwitches, guaranteedCurrent):
        """
        Initialize an interlock.
        :param name: Name of the interlock.
        :param interlockedSwitches: List of interlocked switches
        :param guaranteedCurrent: Minimum guaranteed current capacity of lines at closed switches
        """
        super(DynamicInterlock, self).__init__(name, interlockedSwitches)
        self.guaranteedCurrent = guaranteedCurrent
