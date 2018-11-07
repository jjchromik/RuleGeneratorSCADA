#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents a generator node.
'''
from GridComponents.AbstractNode import AbstractNode
from LoggerUtilities import logCheckPassed, logCheckDescription, logAllChecksPassed, logAllChecksDescription, \
    logDebugCheckValues, logDebugUnknownValues, logError
from StateManagerUtilities import isClose
from ValueStore import ValueNotStoredException


class Generator(AbstractNode):
    def __init__(self, name, linesIn, linesOut, generatedPowerKey=None):
        """
        Initialize a generator.
        :param name: Name of the generator.
        :param linesIn: List of ingoing lines
        :param linesOut: List of outgoing lines
        :param generatedPowerKey: Key for retrieving power state
        """
        super(Generator, self).__init__(name, linesIn, linesOut)
        assert len(linesIn) == 0
        assert len(linesOut) == 1
        self.generatedPowerKey = generatedPowerKey if generatedPowerKey else "%s_P" % self.name.upper()

    def consistencyCheckP5a(self, state):
        """
        This consistency rule checks whether P = I * V holds for the generator.
        :param state: State object (observed or calculated)
        :return: True if consistency rule holds, False otherwise (violation)
        """
        logCheckDescription("P5a", indentation=3)
        passed = True
        try:
            l = self.linesOut[0]
            localVoltage = l.retrieveValue(state, self, "local", "voltage")
            localCurrent = l.retrieveValue(state, self, "local", "current")
            calculatedPower = localVoltage * localCurrent
            generatedPower = state.retrieveValue(self.generatedPowerKey)
            passed = isClose(localVoltage * localCurrent, generatedPower)
            logDebugCheckValues("Generator %s. V=%f,A=%f. V*A=%f (==) P=%f." % (self.name, localVoltage, localCurrent, calculatedPower, generatedPower), passed, indentation=3)
        except ValueNotStoredException, e:
            logDebugUnknownValues(e.message, indentation=3)
        logCheckPassed("P5a", passed, indentation=3)
        return passed

    def executeConsistencyCheck(self, state):
        """
        Execute consistency check over this compnent.
        :param state: State object which contains state information
        """
        logAllChecksDescription("CONSISTENCY", "GENERATOR %s" % self.name, indentation=2)
        checkStatus = dict()
        try:
            checkStatus["P3"] = self.consistencyCheckP3(state)
            checkStatus["P4"] = self.consistencyCheckP4(state)
            checkStatus["P5a"] = self.consistencyCheckP5a(state)
            logAllChecksPassed("CONSISTENCY", "GENERATOR %s" % self.name, all(checkStatus.values()), indentation=2)
        except Exception, e:
            logError("Unknown exception or error: %s" % e.message, indentation=2)
        return checkStatus

    def executeSafetyCheck(self, state):
        """
        Execute safety check over this compnent.
        :param state: State object which contains state information
        """
        logAllChecksDescription("SAFETY", "GENERATOR %s" % self.name, indentation=2)
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
            logAllChecksPassed("SAFETY", "GENERATOR %s" % self.name, all(checkStatus.values()), indentation=2)
        except Exception, e:
            logError("Unknown exception or error: %s" % e.message, indentation=2)
        return checkStatus

    def generateBroConsistencyCheck(self):
        """Generate consistency check bro rules for this compnent."""
        pass

    def generateBroSafetyCheck(self):
        """Generate safety check bro rules for this compnent."""
        pass
