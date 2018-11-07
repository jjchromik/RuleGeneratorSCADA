#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents an abstract interlock.
'''
from GridComponents.Switch import Switch


class AbstractInterlock(object):
    allInterlocks = []

    def __init__(self, name, interlockedSwitches):
        """
        Initialize an interlock.
        :param name: Name of the interlock.
        :param interlockedSwitches: List of interlocked switches
        """
        self.name = name
        assert type(interlockedSwitches) == list
        self.interlockedSwitches = interlockedSwitches
        for switch in self.interlockedSwitches:
            assert type(switch) == Switch
            switch.interlocks.append(self)
        AbstractInterlock.allInterlocks.append(self)


def getAllInterlocksOfType(type):
    """
    Return all interlocks of the given type.
    :param type: DynamicInterlock or StaticInterlock
    :return: List of all respective interlocks
    """
    return [c for c in AbstractInterlock.allInterlocks if isinstance(c, type)]
