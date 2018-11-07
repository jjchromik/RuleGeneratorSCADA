#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents a transformer.
'''
from collections import defaultdict

from GridComponents.AbstractNode import AbstractNode
from LoggerUtilities import logAllChecksPassed, logAllChecksDescription, logCheckDescription, logCheckPassed, \
    logDebugCheckValues, logDebugUnknownValues, logError
from StateManagerUtilities import isClose, isZero
from ValueStore import ValueNotStoredException


class Transformer(AbstractNode):
    transformersByTags = defaultdict(lambda: None)

    def __init__(self, name, linesIn, linesOut, transformerRateFunction, tapPositionKey=None):
        """
        Initialize a transformer.
        :param name: Name of the transformer.
        :param linesIn: List of ingoing lines
        :param linesOut: List of outgoing lines
        :param transformerRateFunction: Function which defines transformer rate in relation to tap position
        :param generatedPowerKey: Key for retrieving tap position
        """
        super(Transformer, self).__init__(name, linesIn, linesOut)
        assert len(linesIn) == 1
        assert len(linesOut) == 1
        assert callable(transformerRateFunction)
        self.rateFunction = transformerRateFunction
        self.tapPositionKey = tapPositionKey if tapPositionKey else "%s_TAP" % self.name.upper()
        Transformer.transformersByTags[self.tapPositionKey] = self

    def consistencyCheckP6a(self, state):
        """
        This consistency rule checks whether the transformation rate is consistent with the voltage measurement.
        :param state: State object (observed or calculated)
        :return: True if consistency rule holds, False otherwise (violation)
        """
        logCheckDescription("P6a", indentation=3)
        passed = True
        if callable(self.rateFunction):
            try:
                measuredInVoltage = self.linesIn[0].retrieveValue(state, self, "local", "voltage")
                measuredOutVoltage = self.linesOut[0].retrieveValue(state, self, "local", "voltage")
                currentTapPosition = state.retrieveValue(self.tapPositionKey)
                if isZero(measuredOutVoltage):
                    passed = True
                    logDebugCheckValues("Transformer %s. Measured input voltage: %fV. Measured output voltage: %fV. Output voltage zero!" %
                                        (self.name, measuredInVoltage, measuredOutVoltage), passed, indentation=3)
                else:
                    try:
                        currentTransformerRate = self.rateFunction(currentTapPosition)
                        expectedMeasuredTransformedOutVoltage = measuredInVoltage / float(currentTransformerRate)
                        if isClose(expectedMeasuredTransformedOutVoltage, measuredOutVoltage):
                            passed = True
                        else:
                            passed = False
                        logDebugCheckValues("Transformer %s. Measured input voltage: %fV. Measured output voltage: %fV. Expected output voltage: %fV." %
                                            (self.name, measuredInVoltage, measuredOutVoltage, expectedMeasuredTransformedOutVoltage), passed, indentation=3)
                    except IndexError:
                        passed = False
                        logDebugCheckValues("Transformer %s. Discrete tap function, tap position %d has no rate defined. " %
                                            (self.name, int(round(currentTapPosition))), passed, indentation=3)
            except ValueNotStoredException, e:
                passed = True
                logDebugUnknownValues(e.message, indentation=3)
        else:
            passed = False
        logCheckPassed("P6a", passed, indentation=3)
        return passed

    def consistencyCheckP6b(self, state):
        """
        This consistency rule checks whether the transformation rate is consistent with the current measurement.
        :param state: State object (observed or calculated)
        :return: True if consistency rule holds, False otherwise (violation)
        """
        logCheckDescription("P6b", indentation=3)
        passed = True
        if callable(self.rateFunction):
            try:
                measuredInCurrent = self.linesIn[0].retrieveValue(state, self, "local", "current")
                measuredOutCurrent = self.linesOut[0].retrieveValue(state, self, "local", "current")
                currentTapPosition = state.retrieveValue(self.tapPositionKey)
                if isZero(measuredInCurrent):
                    passed = True
                    logDebugCheckValues("Transformer %s. No incoming or outgoing current." % (self.name), passed, indentation=3)
                else:
                    try:
                        currentTransformerRate = self.rateFunction(currentTapPosition)
                        expectedMeasuredTransformedOutCurrent = measuredInCurrent * float(currentTransformerRate)
                        if isClose(expectedMeasuredTransformedOutCurrent, measuredOutCurrent):
                            passed = True
                        else:
                            passed = False
                        logDebugCheckValues("Transformer %s. Measured input current: %fA. Measured output current: %fA. Expected output current: %fA." %
                                            (self.name, measuredInCurrent, measuredOutCurrent, expectedMeasuredTransformedOutCurrent), passed, indentation=3)
                    except IndexError:
                        passed = False
                        logDebugCheckValues("Transformer %s. Discrete tap function, tap position %d has no rate defined." %
                                            (self.name, int(round(currentTapPosition))), passed, indentation=3)
                    except ZeroDivisionError:
                        passed = False
                        logDebugCheckValues("Transformer %s. Measured input current: %fA. Measured output current: %fA. (Division by zero, not consistent)." %
                                            (self.name, measuredInCurrent, measuredOutCurrent), passed, indentation=3)
            except ValueNotStoredException, e:
                passed = True
                logDebugUnknownValues(e.message, indentation=3)
        else:
            passed = False
        logCheckPassed("P6b", passed, indentation=3)
        return passed

    def consistencyCheckP7(self, state):
        """
        This consistency rule checks whether the transformer has a rate function defined
        :param state: State object (observed or calculated)
        :return: True if consistency rule holds, False otherwise (violation)
        """
        logCheckDescription("P7", indentation=3)
        passed = False
        if callable(self.rateFunction):
            try:
                currentTapPosition = state.retrieveValue(self.tapPositionKey)
                try:
                    currentTransformerRate = self.rateFunction(currentTapPosition)
                    passed = True
                    logDebugCheckValues("Transformer %s. Transformer rate function defined, tap position valid." % (self.name), passed, indentation=3)
                except:
                    passed = False
                    logDebugCheckValues("Transformer %s. Transformer rate function defined, but tap position invalid." % (self.name), passed, indentation=3)
            except ValueNotStoredException, e:
                passed = True
                logDebugUnknownValues(e.message, indentation=3)
        else:
            passed = False
            logDebugCheckValues("Transformer %s. No transformer rate function defined." % (self.name), passed, indentation=3)
        logCheckPassed("P7", passed, indentation=3)
        return passed

    def safetyCheckR5a(self, state):
        """
        This safety rule checks whether the transformer rate is safe on nominal voltage
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R5a", indentation=3)
        passed = True
        if callable(self.rateFunction):
            try:
                nominalInVoltage = self.linesIn[0].nominalV
                nominalOutVoltage = self.linesOut[0].nominalV
                currentTapPosition = state.retrieveValue(self.tapPositionKey)
                try:
                    currentTransformerRate = self.rateFunction(currentTapPosition)
                    nominalTransformedOutVoltage = nominalInVoltage / float(currentTransformerRate)
                    nominalSafeInterval = (nominalOutVoltage * (1 - self.linesOut[0].voltageBoundaryFactor), nominalOutVoltage * (1 + self.linesOut[0].voltageBoundaryFactor))
                    if nominalSafeInterval[0] <= nominalTransformedOutVoltage <= nominalSafeInterval[1]:
                        currentPassed = True
                    else:
                        currentPassed = False
                    passed = False if not currentPassed else passed
                    logDebugCheckValues(
                        "Transformer %s. Nominal input voltage: %fV. Nominal output voltage: %fV. Transformed nominal output voltage: %fV (should be in [%3.2f;%3.2f])." %
                        (self.name, nominalInVoltage, nominalOutVoltage, nominalTransformedOutVoltage, nominalSafeInterval[0], nominalSafeInterval[1]),
                        currentPassed, indentation=3)
                except IndexError:
                    currentPassed = False
                    passed = False if not currentPassed else passed
                    logDebugCheckValues("Transformer %s. Discrete tap function, tap position %d has no rate defined." %
                                        (self.name, int(round(currentTapPosition))), currentPassed, indentation=3)
            except ValueNotStoredException, e:
                passed = True
                logDebugUnknownValues(e.message, indentation=3)
        else:
            passed = False
            logDebugCheckValues("Transformer %s. Rate function not callable." % self.name, passed, indentation=3)
        logCheckPassed("R5a", passed, indentation=3)
        return passed

    def safetyCheckR5b(self, state):
        """
        This safety rule checks whether the transformer rate is safe on actual voltage
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R5b", indentation=3)
        passed = True
        if callable(self.rateFunction):
            try:
                measuredInVoltage = self.linesIn[0].retrieveValue(state, self, "local", "voltage")
                nominalOutVoltage = self.linesOut[0].nominalV
                currentTapPosition = state.retrieveValue(self.tapPositionKey)
                if isZero(measuredInVoltage):
                    currentPassed = True
                    passed = False if not currentPassed else passed
                    logDebugCheckValues("Transformer %s. Actual input voltage: %fV. Nominal output voltage: %fV. Input voltage is zero." %
                                        (self.name, measuredInVoltage, nominalOutVoltage), currentPassed, indentation=3)
                else:
                    try:
                        currentTransformerRate = self.rateFunction(currentTapPosition)
                        actualTransformedOutVoltage = measuredInVoltage / float(currentTransformerRate)
                        nominalSafeInterval = (nominalOutVoltage * (1 - self.linesOut[0].voltageBoundaryFactor), nominalOutVoltage * (1 + self.linesOut[0].voltageBoundaryFactor))
                        if nominalSafeInterval[0] <= actualTransformedOutVoltage <= nominalSafeInterval[1]:
                            currentPassed = True
                        else:
                            currentPassed = False
                        passed = False if not currentPassed else passed
                        logDebugCheckValues("Transformer %s. Actual input voltage: %fV. Nominal output voltage: %fV. Transformed actual output voltage: %fV (should be in [%3.2f;%3.2f])." %
                                            (self.name, measuredInVoltage, nominalOutVoltage, actualTransformedOutVoltage, nominalSafeInterval[0], nominalSafeInterval[1]), currentPassed, indentation=3)
                    except IndexError:
                        currentPassed = False
                        passed = False if not currentPassed else passed
                        logDebugCheckValues("Transformer %s. Discrete tap function, tap position %d has no rate defined." %
                                            (self.name, int(round(currentTapPosition))), currentPassed, indentation=3)
            except ValueNotStoredException, e:
                passed = True
                logDebugUnknownValues(e.message, indentation=3)
        else:
            passed = False
            logDebugCheckValues("Transformer %s. Rate function not callable." % self.name, passed, indentation=3)
        logCheckPassed("R5b", passed, indentation=3)
        return passed

    def executeConsistencyCheck(self, state):
        """
        Execute consistency check over this compnent.
        :param state: State object which contains state information
        """
        logAllChecksDescription("CONSISTENCY", "TRANSFORMER %s" % self.name, indentation=2)
        checkStatus = dict()
        try:
            checkStatus["P3"] = self.consistencyCheckP3(state)
            checkStatus["P4"] = self.consistencyCheckP4(state)
            checkStatus["P6a"] = self.consistencyCheckP6a(state)
            checkStatus["P6b"] = self.consistencyCheckP6b(state)
            checkStatus["P7"] = self.consistencyCheckP7(state)
            logAllChecksPassed("CONSISTENCY", "TRANSFORMER %s" % self.name, all(checkStatus.values()), indentation=2)
        except Exception, e:
            logError("Unknown exception or error: %s" % e.message, indentation=2)
        return checkStatus

    def executeSafetyCheck(self, state):
        """
        Execute safety check over this compnent.
        :param state: State object which contains state information
        """
        logAllChecksDescription("SAFETY", "TRANSFORMER %s" % self.name, indentation=2)
        checkStatus = dict()
        try:
            checkStatus["R1"] = self.safetyCheckR1(state)
            checkStatus["R2"] = self.safetyCheckR2(state)
            checkStatus["R3"] = self.safetyCheckR3(state)
            checkStatus["R4"] = self.safetyCheckR4(state)
            checkStatus["R5a"] = self.safetyCheckR5a(state)
            checkStatus["R5b"] = self.safetyCheckR5b(state)
            checkStatus["R8a"] = self.safetyCheckR8a(state)
            checkStatus["R8b"] = self.safetyCheckR8b(state)
            checkStatus["R9a"] = self.safetyCheckR9a(state)
            checkStatus["R9b"] = self.safetyCheckR9b(state)
            logAllChecksPassed("SAFETY", "TRANSFORMER %s" % self.name, all(checkStatus.values()), indentation=2)
        except Exception, e:
            logError("Unknown exception or error: %s" % e.message, indentation=2)
        return checkStatus

    def generateBroConsistencyCheck(self):
        """Generate consistency check bro rules for this compnent."""
        pass

    def generateBroSafetyCheck(self):
        """Generate safety check bro rules for this compnent."""
        pass

    def calculateCommandEffects(self, state):
        """
        Calculates the (currently local) effect of a tap position change command.
        :param state: Calculated State object with new tap position
        :return: True if successful, False if calculation was not possible (missing values)
        """
        if callable(self.rateFunction):
            try:
                # get current measurements
                measuredInVoltage = self.linesIn[0].retrieveValue(state, self, "local", "voltage")
                measuredInCurrent = self.linesIn[0].retrieveValue(state, self, "local", "current")
                currentTapPosition = state.retrieveValue(self.tapPositionKey)

                # calculate effect
                currentTransformerRate = self.rateFunction(currentTapPosition)
                expectedMeasuredTransformedOutVoltage = measuredInVoltage / float(currentTransformerRate)
                expectedMeasuredTransformedOutCurrent = measuredInCurrent * float(currentTransformerRate)

                # update calculated state object
                state.updateValue(self.linesOut[0].startMeter.voltageKey, expectedMeasuredTransformedOutVoltage)
                state.updateValue(self.linesOut[0].startMeter.currentKey, expectedMeasuredTransformedOutCurrent)
                return True
            except ValueNotStoredException, e:
                return False
        else:
            return False


def getTransformerByTag(tagName):
    """
    Return the transformer component which contains the given tag.
    :param tagName: Tag name
    :return: Transformer which has the tag
    """
    return Transformer.transformersByTags[tagName]
