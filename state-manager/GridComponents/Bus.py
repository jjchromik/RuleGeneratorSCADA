#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents a bus node.
'''
from GridComponents.AbstractNode import AbstractNode
from LoggerUtilities import logCheckPassed, logCheckDescription, logAllChecksPassed, logAllChecksDescription, \
    logDebugCheckValues, logDebugUnknownValues, logError
from StateManagerUtilities import isClose
from ValueStore import ValueNotStoredException


class Bus(AbstractNode):
    def __init__(self, name, linesIn, linesOut):
        """
        Initialize a bus.
        :param name: Name of the bus.
        :param linesIn: List of ingoing lines
        :param linesOut: List of outgoing lines
        """
        super(Bus, self).__init__(name, linesIn, linesOut)
        assert len(linesIn) > 0
        assert len(linesOut) > 0

    def consistencyCheckP1(self, state):
        """
        This consistency rule checks whether Kirchhoff's current law holds at the bus.
        :param state: State object (observed or calculated)
        :return: True if consistency rule holds, False otherwise (violation)
        """
        logCheckDescription("P1", indentation=3)
        passed = True
        try:
            # compare sum of ingoing current with sum of outgoing current
            sumOfIngoingCurrent = sum([l.retrieveValue(state, self, "local", "current") for l in self.linesIn])
            sumOfOutgoingCurrent = sum([l.retrieveValue(state, self, "local", "current") for l in self.linesOut])
            passed = isClose(sumOfIngoingCurrent, sumOfOutgoingCurrent)
            logDebugCheckValues("Ingoing current: %f (==) Outgoing current: %f." % (sumOfIngoingCurrent, sumOfOutgoingCurrent), passed, indentation=3)
        except ValueNotStoredException, e:
            logDebugUnknownValues(e.message, indentation=3)
        logCheckPassed("P1", passed, indentation=3)
        return passed

    def consistencyCheckP2(self, state):
        """
        This consistency rule checks whether the voltage equals on all meters of a bus.
        Meters with V=0 are excluded as they might be disconnected.
        :param state: State object (observed or calculated)
        :return: True if consistency rule holds, False otherwise (violation)
        """
        logCheckDescription("P2", indentation=3)
        passed = True
        try:
            # check if all measured voltages on bus are approximately equal (or 0 V)
            allMeasuredVoltages = [l.retrieveValue(state, self, "local", "voltage") for l in self.getAllConnectedLines()]
            relevantMeasuredVoltages = [v for v in allMeasuredVoltages if not isClose(v, 0.00)]
            passed = isClose(min(relevantMeasuredVoltages), max(relevantMeasuredVoltages))
            logDebugCheckValues("Minimum V: %f (==) Maximum V: %f." % (min(relevantMeasuredVoltages), max(relevantMeasuredVoltages)), passed, indentation=3)
        except ValueNotStoredException, e:
            logDebugUnknownValues(e.message, indentation=3)
        logCheckPassed("P2", passed, indentation=3)
        return passed

    def executeConsistencyCheck(self, state):
        """
        Execute consistency check over this compnent.
        :param state: State object which contains state information
        """
        logAllChecksDescription("CONSISTENCY", "BUS %s" % self.name, indentation=2)
        checkStatus = dict()
        try:
            checkStatus["P1"] = self.consistencyCheckP1(state)
            checkStatus["P2"] = self.consistencyCheckP2(state)
            checkStatus["P3"] = self.consistencyCheckP3(state)
            checkStatus["P4"] = self.consistencyCheckP4(state)
            logAllChecksPassed("CONSISTENCY", "BUS %s" % self.name, all(checkStatus.values()), indentation=2)
        except Exception, e:
            logError("Unknown exception or error: %s" % e.message, indentation=2)
        return checkStatus

    def executeSafetyCheck(self, state):
        """
        Execute safety check over this compnent.
        :param state: State object which contains state information
        """
        logAllChecksDescription("SAFETY", "BUS %s" % self.name, indentation=2)
        checkStatus = dict()
        try:
            checkStatus["R1"] = self.safetyCheckR1(state)
            checkStatus["R2"] = self.safetyCheckR2(state)
            checkStatus["R3"] = self.safetyCheckR3(state)
            checkStatus["R4"] = self.safetyCheckR4(state)
            checkStatus["R8a"] = self.safetyCheckR8a(state)
            checkStatus["R8b"] = self.safetyCheckR8b(state)
            checkStatus["R9a"] = self.safetyCheckR9a(state)
            checkStatus["R9b"] = self.safetyCheckR9b(state)
            logAllChecksPassed("SAFETY", "BUS %s" % self.name, all(checkStatus.values()), indentation=2)
        except Exception, e:
            logError("Unknown exception or error: %s" % e.message, indentation=2)
        return checkStatus

    def generateBroConsistencyCheck(self):
        """Generate consistency check bro rules for this compnent."""
        pass

    def generateBroSafetyCheck(self):
        """Generate safety check bro rules for this compnent."""
        pass

