#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This abstract class is parent class of every node component of the electrical grid model (bus, generator, consumer, transformer).
It checks and initializes the ingoing and outgoing lines and offers consistency and safety checks that are applicable to all node types.
'''
import time

from DynamicInterlock import DynamicInterlock
from GridComponents.AbstractComponent import AbstractComponent
from GridComponents.PowerLine import PowerLine
from LoggerUtilities import logCheckPassed, logDebugCheckValues, logCheckDescription, logDebugUnknownValues
from StateManagerUtilities import isZero, isClose
from StaticInterlock import StaticInterlock
from ValueStore import ValueNotStoredException


class AbstractNode(AbstractComponent):
    def __init__(self, name, linesIn, linesOut):
        """
        Initialize a node type.
        :param name: Name of the node.
        :param linesIn: List of ingoing lines
        :param linesOut: List of outgoing lines
        """
        super(AbstractNode, self).__init__(name)
        assert isinstance(linesIn, list)
        assert isinstance(linesOut, list)
        self.linesIn = linesIn
        self.linesOut = linesOut
        for l in linesIn:
            assert isinstance(l, PowerLine)
            l.setEndNode(self)
        for l in linesOut:
            assert isinstance(l, PowerLine)
            l.setStartNode(self)

    def consistencyCheckP3(self, state):
        """
        This consistency rule checks that the current is zero if a switch, fuse or protective relay has an open circuit.
        :param state: State object (observed or calculated)
        :return: True if consistency rule holds, False otherwise (violation)
        """
        logCheckDescription("P3", indentation=3)
        passed = True
        openSwitchedLines = []
        for l in self.getAllConnectedLines():
            try:
                if l.getLocalComponent(self, "local", "switch") and not l.retrieveValue(state, self, "local", "switchState"):
                    openSwitchedLines.append(l)
                elif l.getLocalComponent(self, "remote", "switch") and not l.retrieveValue(state, self, "remote", "switchState"):
                    openSwitchedLines.append(l)
                elif l.getLocalComponent(self, "local", "fuse") and not l.retrieveValue(state, self, "local", "fuseState"):
                    openSwitchedLines.append(l)
                elif l.getLocalComponent(self, "remote", "fuse") and not l.retrieveValue(state, self, "remote", "fuseState"):
                    openSwitchedLines.append(l)
                elif l.getLocalComponent(self, "local", "protectiveRelay") and not l.retrieveValue(state, self, "local", "protectiveRelayState"):
                    openSwitchedLines.append(l)
                elif l.getLocalComponent(self, "remote", "protectiveRelay") and not l.retrieveValue(state, self, "remote", "protectiveRelayState"):
                    openSwitchedLines.append(l)
            except ValueNotStoredException, e:
                logDebugUnknownValues(e.message, l.name, indentation=3)
        if len(openSwitchedLines) > 0:
            for l in openSwitchedLines:
                try:
                    # localVoltage = l.retrieveValue(state, self, "local", "voltage")
                    localCurrent = l.retrieveValue(state, self, "local", "current")
                    # remoteVoltage = l.retrieveValue(state, self, "remote", "voltage")
                    remoteCurrent = l.retrieveValue(state, self, "remote", "current")
                    # currentPassed = isZero(localVoltage) and isZero(localCurrent) and isZero(remoteVoltage) and isZero(
                    #    remoteCurrent)
                    currentPassed = isZero(localCurrent) and isZero(remoteCurrent)
                    passed = False if not currentPassed else passed
                    # logDebugCheckValues(
                    #    "Open circuit (switch/fuse/protectiveRelay) on line %s. Local: V=%f (==0.0) AND A=%f (==0.0). Remote: V=%f (==0.0) AND A=%f (==0.0). %s" % (
                    #        l.name, localVoltage, localCurrent, remoteVoltage, remoteCurrent, str(currentPassed)),
                    #    indentation=3)
                    logDebugCheckValues("Open circuit (switch/fuse/protectiveRelay) on line %s. Local: A=%f (==0.0). Remote: A=%f (==0.0)." %
                                        (l.name, localCurrent, remoteCurrent), currentPassed, indentation=3)
                except ValueNotStoredException, e:
                    logDebugUnknownValues(e.message, l.name, indentation=3)
                    try:
                        # localVoltage = l.retrieveValue(state, self, "local", "voltage")
                        localCurrent = l.retrieveValue(state, self, "local", "current")
                        # currentPassed = isZero(localVoltage) and isZero(localCurrent)
                        currentPassed = isZero(localCurrent)
                        passed = False if not currentPassed else passed
                        # logDebugCheckValues(
                        #    "Open circuit (switch/fuse/protectiveRelay) on line %s. Local: V=%f (==0.0) AND A=%f (==0.0). (Remote values unknown) %s" % (
                        #        l.name, localVoltage, localCurrent, str(currentPassed)), indentation=3)
                        logDebugCheckValues("Open circuit (switch/fuse/protectiveRelay) on line %s. Local: A=%f (==0.0). Remote values unknown." %
                                            (l.name, localCurrent), currentPassed, indentation=3)
                    except ValueNotStoredException, e:
                        pass
        else:
            logDebugCheckValues("No open circuit (by switch/fuse/protectiveRelay) found at Bus %s." % (self.name), True, indentation=3)

        logCheckPassed("P3", passed, indentation=3)
        return passed

    def consistencyCheckP4(self, state):
        """
        This consistency rule checks that the voltage and current at the start of a line is the same as at the end.
        :param state: State object (observed or calculated)
        :return: True if consistency rule holds, False otherwise (violation)
        """
        logCheckDescription("P4", indentation=3)
        passed = True
        for l in self.getAllConnectedLines():
            try:
                localVoltage = l.retrieveValue(state, self, "local", "voltage")
                localCurrent = l.retrieveValue(state, self, "local", "current")
                remoteVoltage = l.retrieveValue(state, self, "remote", "voltage")
                remoteCurrent = l.retrieveValue(state, self, "remote", "current")
                currentPassed = isClose(localVoltage, remoteVoltage) and isClose(localCurrent, remoteCurrent)
                passed = False if not currentPassed else passed
                logDebugCheckValues("Line %s. Local: V=%f,A=%f (==) Remote: V=%f,A=%f." % (l.name, localVoltage, localCurrent, remoteVoltage, remoteCurrent), currentPassed, indentation=3)
            except ValueNotStoredException, e:
                logDebugUnknownValues(e.message, l.name, indentation=3)
        logCheckPassed("P4", passed, indentation=3)
        return passed

    def safetyCheckR1(self, state):
        """
        This safety rule checks that the current is below the maximal safe current threshold for a power line
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R1", indentation=3)
        passed = True
        for l in self.getAllConnectedLines():
            try:
                localCurrent = l.retrieveValue(state, self, "local", "current")
                currentPassed = localCurrent <= l.maxI
                passed = False if not currentPassed else passed
                logDebugCheckValues("Line %s. A=%f (<= maxI = %f)." % (l.name, localCurrent, l.maxI), currentPassed, indentation=3)
            except ValueNotStoredException, e:
                logDebugUnknownValues(e.message, l.name, indentation=3)
        logCheckPassed("R1", passed, indentation=3)
        return passed

    def safetyCheckR2(self, state):
        """
        This safety rule checks that the voltage is within its allowed interval around the nominal voltage
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R2", indentation=3)
        passed = True
        for l in self.getAllConnectedLines():
            try:
                safeInterval = (l.nominalV * (1 - l.voltageBoundaryFactor), l.nominalV * (1 + l.voltageBoundaryFactor))
                localVoltage = l.retrieveValue(state, self, "local", "voltage")
                if not isZero(localVoltage):
                    currentPassed = safeInterval[0] <= localVoltage <= safeInterval[1]
                    passed = False if not currentPassed else passed
                    logDebugCheckValues("Line %s. Local: V=%f (in [%3.2f;%3.2f])." % (l.name, localVoltage, safeInterval[0], safeInterval[1]), currentPassed, indentation=3)
            except ValueNotStoredException, e:
                logDebugUnknownValues(e.message, l.name, indentation=3)
        logCheckPassed("R2", passed, indentation=3)
        return passed

    def safetyCheckR3(self, state):
        """
        This safety rule checks whether all fuses and protective relays are closed.
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R3", indentation=3)
        passed = True
        for l in self.getAllConnectedLines():
            localFuse = l.getLocalComponent(self, "local", "fuse")
            if localFuse:
                try:
                    fuseState = state.retrieveValue(localFuse.stateKey)
                    if not fuseState:
                        currentPassed = False
                        logDebugCheckValues("Line %s. Fuse found. Fuse molten." % (l.name), currentPassed, indentation=3)
                    else:
                        currentPassed = True
                        logDebugCheckValues("Line %s. Fuse found. Fuse okay." % (l.name), currentPassed, indentation=3)
                except ValueNotStoredException, e:
                    currentPassed = True
                    logDebugUnknownValues(e.message, l.name, indentation=3)
                    logDebugCheckValues("Line %s. Fuse found. Fuse state unknown." % (l.name), currentPassed, indentation=3)
            else:
                currentPassed = True
                logDebugCheckValues("Line %s. No local fuse." % (l.name), currentPassed, indentation=3)
            passed = False if not currentPassed else passed

            localProtectiveRelay = l.getLocalComponent(self, "local", "protectiveRelay")
            if localProtectiveRelay:
                try:
                    protectiveRelayState = state.retrieveValue(localProtectiveRelay.stateKey)
                    if not protectiveRelayState:
                        currentPassed = False
                        logDebugCheckValues("Line %s. Protective relay found. Protective relay open." % (l.name), currentPassed, indentation=3)
                    else:
                        currentPassed = True
                        logDebugCheckValues("Line %s. Protective relay found. Protective relay closed." % (l.name), currentPassed, indentation=3)
                except ValueNotStoredException, e:
                    currentPassed = True
                    logDebugUnknownValues(e.message, l.name, indentation=3)
                    logDebugCheckValues("Line %s. Protective relay found. Protective relay state unknown." % (l.name), currentPassed, indentation=3)
            else:
                currentPassed = True
                logDebugCheckValues("Line %s. No local Protective relay." % (l.name), currentPassed, indentation=3)
        passed = False if not currentPassed else passed
        logCheckPassed("R3", passed, indentation=3)
        return passed

    def safetyCheckR4(self, state):
        """
        This safety rule checks whether all lines connected to fuses and protective relays have current below the cutting current
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R4", indentation=3)
        passed = True
        for l in self.getAllConnectedLines():
            localFuse = l.getLocalComponent(self, "local", "fuse")
            if localFuse:
                try:
                    currentNow = localFuse.connectedLine.retrieveValue(state, self, "local", "current")
                    if currentNow > localFuse.cuttingI:
                        try:
                            localMeter = l.getLocalComponent(self, "local", "meter")
                            currentFuseDelayAgo = state.retrieveValueBefore(localMeter.currentKey,
                                                                            time.time() - localFuse.cuttingT)
                            if currentFuseDelayAgo > localFuse.cuttingI:
                                currentPassed = False
                                logDebugCheckValues("Line %s. Fuse found. Fuse broken? Current over %d seconds (fuse delay) above fuse current limit  (%f < %f)." %
                                                    (l.name, localFuse.cuttingT, currentNow, localFuse.cuttingI), currentPassed, indentation=3)
                            else:
                                currentPassed = False
                                logDebugCheckValues("Line %s. Fuse found. Current not okay  (%f < %f), but was okay before fuse delay (%d seconds ago)." %
                                                    (l.name, currentNow, localFuse.cuttingI, localFuse.cuttingT), currentPassed, indentation=3)
                        except ValueNotStoredException, e:
                            currentPassed = False
                            logDebugCheckValues("Line %s. Fuse found. Current not okay  (%f < %f). Current %d seconds ago unknown." %
                                                (l.name, currentNow, localFuse.cuttingI, localFuse.cuttingT), currentPassed, indentation=3)
                    else:
                        currentPassed = True
                        logDebugCheckValues("Line %s. Fuse found. Current okay (%f < %f)." % (l.name, currentNow, localFuse.cuttingI), currentPassed, indentation=3)
                except ValueNotStoredException, e:
                    currentPassed = True
                    logDebugUnknownValues(e.message, l.name, indentation=3)
                    logDebugCheckValues("Line %s. Fuse found. Current unknown." % (l.name), currentPassed, indentation=3)
            else:
                currentPassed = True
                logDebugCheckValues("Line %s. No local fuse." % (l.name), currentPassed, indentation=3)
            passed = False if not currentPassed else passed

            localProtectiveRelay = l.getLocalComponent(self, "local", "protectiveRelay")
            if localProtectiveRelay:
                try:
                    currentNow = localProtectiveRelay.connectedLine.retrieveValue(state, self, "local", "current")
                    if currentNow > localProtectiveRelay.cuttingI:
                        try:
                            localMeter = l.getLocalComponent(self, "local", "meter")
                            currentProtectiveRelayDelayAgo = state.retrieveValueBefore(localMeter.currentKey,
                                                                                       time.time() - localProtectiveRelay.cuttingT)
                            if currentProtectiveRelayDelayAgo > localProtectiveRelay.cuttingI:
                                currentPassed = False
                                logDebugCheckValues("Line %s. Protective relay found. Protective relay broken? Current over %d seconds (protective relay delay) above protective relay current limit  (%f > %f)." %
                                                    (l.name, localProtectiveRelay.cuttingT, currentNow, localProtectiveRelay.cuttingI), currentPassed, indentation=3)
                            else:
                                currentPassed = False
                                logDebugCheckValues("Line %s. Protective relay found. Current not okay (%f > %f), but was okay before protective relay delay (%d seconds ago)." %
                                                    (l.name, currentNow, localProtectiveRelay.cuttingI, localProtectiveRelay.cuttingT), currentPassed, indentation=3)
                        except ValueNotStoredException, e:
                            currentPassed = False
                            logDebugCheckValues("Line %s. Protective relay found. Current not okay (%f > %f). Current %d seconds ago unknown." %
                                                (l.name, currentNow, localProtectiveRelay.cuttingI, localProtectiveRelay.cuttingT), currentPassed, indentation=3)
                    else:
                        currentPassed = True
                        logDebugCheckValues("Line %s. Protective relay found. Current okay (%f < %f)." % (l.name, currentNow, localProtectiveRelay.cuttingI), currentPassed, indentation=3)
                except ValueNotStoredException, e:
                    currentPassed = True
                    logDebugUnknownValues(e.message, l.name, indentation=3)
                    logDebugCheckValues("Line %s. Protective relay found. Current unknown." % (l.name), currentPassed, indentation=3)
            else:
                currentPassed = True
                logDebugCheckValues("Line %s. No local protective relay." % (l.name), currentPassed, indentation=3)
            passed = False if not currentPassed else passed
        logCheckPassed("R4", passed, indentation=3)
        return passed

    def safetyCheckR8a(self, state):
        """
        This safety rule checks whether the voltage set points are safe
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R8a", indentation=3)
        passed = True
        for l in self.getAllConnectedLines():
            try:
                localVoltageSetPoint = l.retrieveValue(state, self, "local", "setPointV")
                allowedSetPointInterval = (l.nominalV * 0.90, l.nominalV * 1.10)
                currentPassed = allowedSetPointInterval[0] <= localVoltageSetPoint <= allowedSetPointInterval[1]
                passed = False if not currentPassed else passed
                logDebugCheckValues("Line %s. Voltage set point = %fV (in [%5.2f,%5.2f]V)." %
                                    (l.name, localVoltageSetPoint, allowedSetPointInterval[0], allowedSetPointInterval[1]), currentPassed, indentation=3)
            except ValueNotStoredException, e:
                logDebugUnknownValues(e.message, l.name, indentation=3)
        logCheckPassed("R8a", passed, indentation=3)
        return passed

    def safetyCheckR8b(self, state):
        """
        This safety rule checks whether the current set points are safe
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R8b", indentation=3)
        passed = True
        for l in self.getAllConnectedLines():
            try:
                localCurrentSetPoint = l.retrieveValue(state, self, "local", "setPointI")
                allowedSetPointInterval = (l.maxI * 0.90, l.maxI * 1.10)
                currentPassed = allowedSetPointInterval[0] <= localCurrentSetPoint <= allowedSetPointInterval[1]
                passed = False if not currentPassed else passed
                logDebugCheckValues("Line %s. Current set point = %fA (in [%5.2f,%5.2f]A)." %
                                    (l.name, localCurrentSetPoint, allowedSetPointInterval[0], allowedSetPointInterval[1]), currentPassed, indentation=3)
            except ValueNotStoredException, e:
                logDebugUnknownValues(e.message, l.name, indentation=3)
        logCheckPassed("R8b", passed, indentation=3)
        return passed

    def safetyCheckR9a(self, state):
        """
        This safety rule checks that static interlocks are not violated.
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R9a", indentation=3)
        passed = True
        for l in self.getAllConnectedLines():
            try:
                localSwitch = l.getLocalComponent(self, "local", "switch")
                if not l.retrieveValue(state, self, "local", "switchState"):
                    if localSwitch and localSwitch.interlocks:
                        for interlock in localSwitch.interlocks:
                            if isinstance(interlock, StaticInterlock):
                                try:
                                    switchStates = [state.retrieveValue(s.stateKey) for s in
                                                    interlock.interlockedSwitches]
                                    if sum(switchStates) >= interlock.guaranteedClosedSwitches:
                                        currentPassed = True
                                    else:
                                        currentPassed = False
                                    passed = False if not currentPassed else passed
                                    logDebugCheckValues("Open switch on line %s. Switch is interlocked. Interlock switch states: %s (>= %d)." %
                                                        (l.name, str(switchStates), interlock.guaranteedClosedSwitches), currentPassed, indentation=3)
                                except ValueNotStoredException, e:
                                    currentPassed = True
                                    logDebugUnknownValues(e.message, l.name, indentation=3)
                    else:
                        currentPassed = True
                        logDebugCheckValues("Open switch %s found at Bus %s, but no interlocks defined for that switch." %
                                            (localSwitch.name, self.name), currentPassed, indentation=3)
                else:
                    currentPassed = True
                    logDebugCheckValues("Local switch %s at Bus %s closed." % (localSwitch.name, self.name), currentPassed, indentation=3)
            except ValueNotStoredException, e:
                currentPassed = True
                logDebugUnknownValues(e.message, indentation=3)
            passed = False if not currentPassed else passed
        logCheckPassed("R9a", passed, indentation=3)
        return passed

    def safetyCheckR9b(self, state):
        """
        This safety rule checks that dynamic interlocks are not violated.
        :param state: State object (observed or calculated)
        :return: True if safety rule holds, False otherwise (violation)
        """
        logCheckDescription("R9b", indentation=3)
        passed = True
        for l in self.getAllConnectedLines():
            try:
                localSwitch = l.getLocalComponent(self, "local", "switch")
                if not l.retrieveValue(state, self, "local", "switchState"):
                    if localSwitch and localSwitch.interlocks:
                        for interlock in localSwitch.interlocks:
                            if isinstance(interlock, DynamicInterlock):
                                try:
                                    switchStates = [state.retrieveValue(s.stateKey) for s in
                                                    interlock.interlockedSwitches]
                                    switchCurrent = [s.connectedLine.maxI for s in
                                                     interlock.interlockedSwitches]
                                    zippedSwitchInfos = zip(switchStates, switchCurrent)
                                    if sum([switchState * current for switchState, current in
                                            zippedSwitchInfos]) >= interlock.guaranteedCurrent:
                                        currentPassed = True
                                    else:
                                        currentPassed = False
                                    passed = False if not currentPassed else passed
                                    logDebugCheckValues("Open switch on line %s. Switch is interlocked. Interlock switch states + current capacities: %s (>= %dA)." %
                                                        (l.name, str(zippedSwitchInfos), interlock.guaranteedCurrent,), currentPassed, indentation=3)
                                except ValueNotStoredException, e:
                                    logDebugUnknownValues(e.message, l.name, indentation=3)
                    else:
                        currentPassed = True
                        logDebugCheckValues("Open switch %s found at Bus %s, but no interlocks defined for that switch." %
                                            (localSwitch.name, self.name), currentPassed, indentation=3)
                else:
                    currentPassed = True
                    logDebugCheckValues("Local switch %s at Bus %s closed." % (localSwitch.name, self.name), currentPassed, indentation=3)
            except ValueNotStoredException, e:
                currentPassed = True
                logDebugUnknownValues(e.message, indentation=3)
            passed = False if not currentPassed else passed
        logCheckPassed("R9b", passed, indentation=3)
        return passed

    def getAllConnectedLines(self):
        """
        Return a list of all connected power lines.
        :return: List of all connected power lines (ingoing and outgoing)
        """
        return self.linesIn + self.linesOut

    def executeConsistencyCheck(self, state):
        """
        Execute consistency check over this compnent.
        (Function stub for subclasses)
        :param state: State object which contains state information
        """
        pass

    def executeSafetyCheck(self, state):
        """
        Execute safety check over this compnent.
        (Function stub for subclasses)
        :param state: State object which contains state information
        """
        pass

    def generateBroConsistencyCheck(self):
        """
        Generate consistency check bro rules for this compnent.
        Function stub for subclasses
        """
        pass

    def generateBroSafetyCheck(self):
        """
        Generate safety check bro rules for this compnent.
        Function stub for subclasses
        """
        pass
