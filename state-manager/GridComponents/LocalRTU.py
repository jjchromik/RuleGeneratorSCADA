#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents a RTU.
'''
from GridComponents.AbstractComponent import getAllComponentsOfType
from GridComponents.Consumer import Consumer
from GridComponents.Generator import Generator
from LoggerUtilities import logCheckPassed, logCheckDescription, logAllChecksDescription, logAllChecksPassed, \
    logDebugCheckValues, logDebugUnknownValues, logError
from StateManagerUtilities import isClose, isZero
from ValueStore import ValueNotStoredException


class LocalRTU:
    def __init__(self, name, controlledNodes):
        """
        Initialize a RTU.
        :param name: Name of the RTU.
        :param controlledNodes: List of nodes that this RTU controlls
        """
        assert name
        assert controlledNodes and isinstance(controlledNodes, list)
        self.name = name
        self.controlledNodes = controlledNodes

    def safetyCheckR6(self, state):
        """
        This safety rule checks whether all consumers are connected to the power grid
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R6", indentation=2)
        passed = True
        for l in getAllComponentsOfType(Consumer):
            if len(l.linesIn) == 0:
                try:
                    consumedPower = (-1) * state.retrieveValue(l.consumedPowerKey)
                    if isZero(consumedPower):
                        currentPassed = True
                        passed = False if not currentPassed else passed
                        logDebugCheckValues("Consumer %s connected to no line, and no power consumed. %fW" % (l.name, consumedPower), currentPassed, indentation=3)
                    else:
                        currentPassed = False
                        passed = False if not currentPassed else passed
                        logDebugCheckValues("Consumer %s connected to no line, but power consumed. %fW" % (l.name, consumedPower), currentPassed, indentation=3)
                except ValueNotStoredException, e:
                    logDebugUnknownValues(e.message, l.name, indentation=3)
            elif len(l.linesIn) == 1:
                try:
                    consumedPower = (-1) * state.retrieveValue(l.consumedPowerKey)
                    localVoltage = l.linesIn[0].retrieveValue(state, l, "local", "voltage")
                    localSwitch = l.linesIn[0].retrieveValue(state, l, "local", "switchState")
                    remoteSwitch = l.linesIn[0].retrieveValue(state, l, "remote", "switchState")
                    currentPassed = localSwitch and remoteSwitch and not isZero(localVoltage)
                    passed = False if not currentPassed else passed
                    logDebugCheckValues("Consumer %s connected to power supply. Local Switch: %s (== True). Remote Switch: %s (== True). V=%f (>0) P=%fW." %
                                        (l.name, localSwitch, remoteSwitch, localVoltage, consumedPower), currentPassed, indentation=3)
                except ValueNotStoredException, e:
                    logDebugUnknownValues(e.message, l.name, indentation=3)
                    try:
                        consumedPower = (-1) * state.retrieveValue(l.consumedPowerKey)
                        localVoltage = l.linesIn[0].retrieveValue(state, l, "local", "voltage")
                        localSwitch = l.linesIn[0].retrieveValue(state, l, "local", "switchState")
                        currentPassed = localSwitch and not isZero(localVoltage)
                        passed = False if not currentPassed else passed
                        logDebugCheckValues("Consumer %s connected to power supply. Local Switch: %s (== True). Remote Switch unknown. V=%f (>0) P=%fW." %
                                            (l.name, localSwitch, localVoltage, consumedPower), currentPassed, indentation=3)
                    except ValueNotStoredException, e:
                        pass
            else:
                currentPassed = False
                passed = False if not currentPassed else passed
        logCheckPassed("R6", passed, indentation=2)
        return passed

    def safetyCheckR7(self, state):
        """
        This safety rule checks whether the global generated power equals the global consumed power
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R7", indentation=2)
        passed = True
        try:
            sumOfGeneratedPower = sum(
                [state.retrieveValue(g.generatedPowerKey) for g in getAllComponentsOfType(Generator)])
            sumOfConsumedPower = (-1) * sum(
                [state.retrieveValue(c.consumedPowerKey) for c in getAllComponentsOfType(Consumer)])
            passed = isClose(sumOfGeneratedPower, sumOfConsumedPower)
            logDebugCheckValues("Global Generated power: %f (==) Global Consumed power: %f." % (sumOfGeneratedPower, sumOfConsumedPower), passed, indentation=3)
        except ValueNotStoredException, e:
            logDebugUnknownValues(e.message, indentation=3)
        logCheckPassed("R7", passed, indentation=2)
        return passed

    def executeFullConsistencyCheck(self, state):
        """
        Execute consistency check over all compnents connected to this RTU.
        :param state: State object which contains state information
        """
        logAllChecksDescription("CONSISTENCY", "RTU %s" % self.name, indentation=1)
        checkStatus = dict()
        try:
            for n in self.controlledNodes:
                checkStatus[n.name] = all(n.executeConsistencyCheck(state).values())
            logAllChecksPassed("CONSISTENCY", "RTU %s" % self.name, all(checkStatus.values()), indentation=1)
        except Exception, e:
            logError("Unknown exception or error: %s" % e.message, indentation=1)
        return checkStatus

    def executeFullSafetyCheck(self, state):
        """
        Execute safety check over all compnents connected to this RTU.
        :param state: State object which contains state information
        """
        logAllChecksDescription("SAFETY", "RTU %s" % self.name, indentation=1)
        checkStatus = dict()
        try:
            for n in self.controlledNodes:
                checkStatus[n.name] = all(n.executeSafetyCheck(state).values())
            checkStatus["R6"] = self.safetyCheckR6(state)
            checkStatus["R7"] = self.safetyCheckR7(state)
            logAllChecksPassed("SAFETY", "RTU %s" % self.name, all(checkStatus.values()), indentation=1)
        except Exception, e:
            logError("Unknown exception or error: %s" % e.message, indentation=1)
        return checkStatus

    def generateFullBroConsistencyCheck(self):
        """Generate consistency check bro rules for this compnent."""
        for n in self.controlledNodes:
            n.generateBroConsistencyCheck()

    def generateFullBroSafetyCheck(self):
        """Generate safety check bro rules for this compnent."""
        for n in self.controlledNodes:
            n.generateBroSafetyCheck()
