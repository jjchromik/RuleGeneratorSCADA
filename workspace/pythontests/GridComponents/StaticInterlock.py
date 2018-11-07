#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents an static interlock.
'''
from GridComponents.AbstractInterlock import AbstractInterlock


class StaticInterlock(AbstractInterlock):
    def __init__(self, name, interlockedSwitches, guaranteedClosedSwitches=1):
        """
        Initialize a static interlock.
        :param name: Name of the interlock.
        :param interlockedSwitches: List of interlocked switches
        :param guaranteedClosedSwitches: Minimum guaranteed number of closed switches
        """
        super(StaticInterlock, self).__init__(name, interlockedSwitches)
        self.guaranteedClosedSwitches = guaranteedClosedSwitches
