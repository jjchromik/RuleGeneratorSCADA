#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents a switch.
'''
from collections import defaultdict

from GridComponents.AbstractDecorator import AbstractDecorator
from StateManagerUtilities import isZero
from ValueStore import ValueNotStoredException


class Switch(AbstractDecorator):
    switchesByTags = defaultdict(lambda: None)

    def __init__(self, name, stateKey=None):
        """
        Initialize a switch.
        :param name: Name of the meter.
        :param stateKey: Key for retrieving switch state
        """
        super(Switch, self).__init__(name)
        self.stateKey = stateKey if stateKey else "%s_STATE" % self.name.upper()
        Switch.switchesByTags[self.stateKey] = self
        self.interlocks = []

    def calculateCommandEffects(self, state):
        """
        Calculates the (currently local) effect of a switch position change.
        :param state: Calculated State object with switch position
        :return: True if successful, False if calculation was not possible (missing values)
        """
        try:
            newPosition = state.retrieveValue(self.stateKey)
            if newPosition:
                # Switch close
                # No chance to calculate this??
                # Adverse effects possible? (yes, but not very probable?)
                return True
            else:
                # Switch open
                if self.connectedLine.startSwitch == self:
                    removedCurrent = state.retrieveValue(self.connectedLine.startMeter.currentKey)
                    state.updateValue(self.connectedLine.startMeter.currentKey, 0.0)
                    state.updateValue(self.connectedLine.endMeter.currentKey, 0.0)
                    affectedNode = self.connectedLine.startNode
                    try:
                        affectedLines = [l for l in affectedNode.linesOut if state.retrieveValue(l.startSwitch.stateKey)]
                        endNodes = defaultdict(lambda: 0)
                        for l in affectedLines:
                            endNodes[l.endNode.name] = endNodes[l.endNode.name] + 1
                        for l in affectedLines:
                            try:
                                measuredCurrent = state.retrieveValue(l.startMeter.currentKey)
                                # split between lines with same destination
                                if not isZero(measuredCurrent):
                                    state.updateValue(l.startMeter.currentKey, measuredCurrent + removedCurrent / endNodes[l.endNode.name])
                            except ValueNotStoredException, e:
                                pass
                    except:
                        for l in affectedNode.linesOut:
                            try:
                                measuredCurrent = state.retrieveValue(l.startMeter.currentKey)
                                # worst case for every line
                                if not isZero(measuredCurrent):
                                    state.updateValue(l.startMeter.currentKey, measuredCurrent + removedCurrent)
                            except ValueNotStoredException, e:
                                pass
                else:
                    removedCurrent = state.retrieveValue(self.connectedLine.endMeter.currentKey)
                    state.updateValue(self.connectedLine.startMeter.currentKey, 0.0)
                    state.updateValue(self.connectedLine.endMeter.currentKey, 0.0)
                    affectedNode = self.connectedLine.endNode
                    try:
                        affectedLines = [l for l in affectedNode.linesIn if state.retrieveValue(l.endSwitch.stateKey)]
                        startNodes = defaultdict(lambda: 0)
                        for l in affectedLines:
                            startNodes[l.startNode.name] = startNodes[l.startNode.name] + 1
                        for l in affectedLines:
                            try:
                                measuredCurrent = state.retrieveValue(l.endMeter.currentKey)
                                # split between lines with same destination
                                if not isZero(measuredCurrent):
                                    state.updateValue(l.endMeter.currentKey, measuredCurrent + removedCurrent / startNodes[l.startNode.name])
                            except ValueNotStoredException, e:
                                pass
                    except:
                        for l in affectedNode.linesIn:
                            try:
                                measuredCurrent = state.retrieveValue(l.endMeter.currentKey)
                                # worst case for every line
                                if not isZero(measuredCurrent):
                                    state.updateValue(l.endMeter.currentKey, measuredCurrent + removedCurrent)
                            except ValueNotStoredException, e:
                                pass
                return True
        except ValueNotStoredException, e:
            return False


def getSwitchByTag(tagName):
    """
    Return the switch component which contains the given tag.
    :param tagName: Tag name
    :return: Switch which has the tag
    """
    return Switch.switchesByTags[tagName]
