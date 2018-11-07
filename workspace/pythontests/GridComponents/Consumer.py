#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents a consumer node.
'''
from GridComponents.AbstractNode import AbstractNode
from LoggerUtilities import logCheckPassed, logCheckDescription, logAllChecksPassed, logAllChecksDescription, \
    logDebugCheckValues, logDebugUnknownValues, logError
from StateManagerUtilities import isClose
from ValueStore import ValueNotStoredException


class Consumer(AbstractNode):
    def __init__(self, name, linesIn, linesOut, consumedPowerKey=None):
        """
        Initialize a consumer.
        :param name: Name of the consumer.
        :param linesIn: List of ingoing lines
        :param linesOut: List of outgoing lines
        :param generatedPowerKey: Key for retrieving power state
        """
        super(Consumer, self).__init__(name, linesIn, linesOut)
        assert len(linesIn) == 1
        assert len(linesOut) == 0
        self.consumedPowerKey = consumedPowerKey if consumedPowerKey else "%s_P" % self.name.upper()

    def consistencyCheckP5b(self, state):
        """
        This consistency rule checks whether P = I * V holds for the consumer.
        :param state: State object (observed or calculated)
        :return: True if consistency rule holds, False otherwise (violation)
        """
        logCheckDescription("P5b", indentation=3)
        passed = True
        try:
            l = self.linesIn[0]
            localVoltage = l.retrieveValue(state, self, "local", "voltage")
            localCurrent = l.retrieveValue(state, self, "local", "current")
            calculatedPower = localVoltage * localCurrent
            consumedPower = (-1) * state.retrieveValue(self.consumedPowerKey)
            passed = isClose(calculatedPower, consumedPower)
            logDebugCheckValues("Consumer %s. V=%f,A=%f. V*A=%f (==) P=%f." % (self.name, localVoltage, localCurrent, calculatedPower, consumedPower), passed, indentation=3)
        except ValueNotStoredException, e:
            logDebugUnknownValues(e.message, indentation=3)
        logCheckPassed("P5b", passed, indentation=3)
        return passed

    def executeConsistencyCheck(self, state):
        """
        Execute consistency check over this compnent.
        :param state: State object which contains state information
        """
        logAllChecksDescription("CONSISTENCY", "CONSUMER %s" % self.name, indentation=2)
        checkStatus = dict()
        try:
            checkStatus["P3"] = self.consistencyCheckP3(state)
            checkStatus["P4"] = self.consistencyCheckP4(state)
            checkStatus["P5b"] = self.consistencyCheckP5b(state)
            logAllChecksPassed("CONSISTENCY", "CONSUMER %s" % self.name, all(checkStatus.values()), indentation=2)
        except Exception, e:
            logError("Unknown exception or error: %s" % e.message, indentation=2)
        return checkStatus

    def executeSafetyCheck(self, state):
        """
        Execute safety check over this compnent.
        :param state: State object which contains state information
        """
        logAllChecksDescription("SAFETY", "CONSUMER %s" % self.name, indentation=2)
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
            logAllChecksPassed("SAFETY", "CONSUMER %s" % self.name, all(checkStatus.values()), indentation=2)
        except Exception, e:
            logError("Unknown exception or error: %s" % e.message, indentation=2)
        return checkStatus

    def generateBroConsistencyCheck(self):
        """Generate consistency check bro rules for this compnent."""
        pass

    def generateBroSafetyCheck(self):
        """Generate safety check bro rules for this compnent."""
        pass
