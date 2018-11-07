#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents a meter.
'''
from collections import defaultdict

from GridComponents.AbstractDecorator import AbstractDecorator


class Meter(AbstractDecorator):
    meterBySetPointTags = defaultdict(lambda: None)

    def __init__(self, name, currentKey=None, voltageKey=None, setPointIKey=None, setPointVKey=None):
        """
        Initialize a meter.
        :param name: Name of the meter.
        :param currentKey: Key for retrieving measured current state
        :param voltageKey: Key for retrieving measured voltage state
        """
        super(Meter, self).__init__(name)
        self.currentKey = currentKey if currentKey else "%s_I" % self.name.upper()
        self.voltageKey = voltageKey if voltageKey else "%s_V" % self.name.upper()
        self.setPointIKey = setPointIKey if setPointIKey else "%s_SP_I" % self.name.upper()
        self.setPointVKey = setPointVKey if setPointVKey else "%s_SP_V" % self.name.upper()
        Meter.meterBySetPointTags[self.setPointIKey] = self
        Meter.meterBySetPointTags[self.setPointVKey] = self


def getMeterBySetPointTag(tagName):
    """
    Return the meter component which contains the given tag.
    :param tagName: Tag name
    :return: Meter which has the tag
    """
    return Meter.meterBySetPointTags[tagName]
