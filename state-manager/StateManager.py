#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

The state manager listens ons a local python broccoli binding for bro events that indicate either a new reading or a new command.
Its purpose is the management of the local observed system state T_{o} and the calculation of the anticipated state T_{c}.
Depending on the result of the consistency checks (P) and the safety requirement checks (R) actions are expressed as an alert to the system operator.
'''
import logging
import sys
import time
from threading import Lock

from GridComponents.Meter import getMeterBySetPointTag
from GridComponents.Switch import getSwitchByTag
from GridComponents.Transformer import getTransformerByTag
from LoggerUtilities import initializeLogging
from StateManagerUtilities import formatTimestamp, normalize_value, doublefy_value, KeyPoller
from TestUtilities import checkTopology
from ValueStore import ValueStore, loadValuesFromFile, saveValuesToFile

sys.path.append('/usr/local/lib/python')
import broccoli

# from broccoli import *  # @UnusedWildImport

BROCCOLI_HOST = "127.0.0.1"
BROCCOLI_PORT = 47758
BROCCOLI_CONNECT = "%s:%d" % (BROCCOLI_HOST, BROCCOLI_PORT)
BROCCOLI_MAIN_LOOP_SLEEP = 0.001
logger = logging.getLogger(__name__)
lock = Lock()
broccoliConnection = None
scenario = None
topology = None
observedValuesStore = None
lastValueUpdate = None
lastEvaluatedCommand = (None, None)
receivedCount = 0


def evaluateCommand(tagName, value):
    """
    Evaluate the safety of a command.
    :param tagName: Tag name that is changed with the command
    :param value: New value
    """
    global observedValuesStore
    logger.warning("Command detected: Set %s to %s" % (tagName, str(value)))
    try:
        calculatedState = observedValuesStore.getCopy()
        calculatedState.updateValue(tagName, value)
        meter = getMeterBySetPointTag(tagName)
        transformer = getTransformerByTag(tagName)
        switch = getSwitchByTag(tagName)
        if meter:
            if tagName == meter.setPointVKey:
                logger.warning("(Voltage set point change)")
                logger.info("Observed state evaluation:")
                resultObserved = meter.connectedNode.safetyCheckR8a(observedValuesStore)
                logger.info("Calculated state evaluation:")
                resultCalculated = meter.connectedNode.safetyCheckR8a(calculatedState)
                logger.info("Safety before command (R8a): %s" % resultObserved)
                logger.info("Safety after command (R8a): %s" % resultCalculated)
                if resultCalculated:
                    logger.warning("New set point is safe.")
                else:
                    logger.warning("New set point is NOT safe.")
            else:
                logger.warning("(Current set point change)")
                logger.info("Observed state evaluation:")
                resultObserved = meter.connectedNode.safetyCheckR8b(observedValuesStore)
                logger.info("Calculated state evaluation:")
                resultCalculated = meter.connectedNode.safetyCheckR8b(calculatedState)
                logger.info("Safety before command (R8b): %s" % resultObserved)
                logger.info("Safety after command (R8b): %s" % resultCalculated)
                if resultCalculated:
                    logger.warning("New set point is safe.")
                else:
                    logger.warning("New set point is NOT safe.")
        elif transformer:
            logger.warning("(Transformer tap position change)")
            if transformer.calculateCommandEffects(calculatedState):
                logger.info("Observed state evaluation:")
                resultObserved = transformer.executeSafetyCheck(observedValuesStore)
                observedSafety = resultObserved["R1"] and resultObserved["R2"] and resultObserved["R4"] and resultObserved["R5a"] and resultObserved["R5b"]
                logger.info("Calculated state evaluation:")
                resultCalculated = transformer.executeSafetyCheck(calculatedState)
                calculatedSafety = resultCalculated["R1"] and resultCalculated["R2"] and resultCalculated["R4"] and resultCalculated["R5a"] and resultCalculated["R5b"]
                logger.info("Safety before command (R1,R2,R4,R5a,R5b): %s" % observedSafety)
                logger.info("Safety after command (R1,R2,R4,R5a,R5b): %s" % calculatedSafety)
                if calculatedSafety:
                    logger.warning("New transformer tap position is safe.")
                else:
                    if observedSafety:
                        logger.warning("New transformer tap position is NOT safe.")
                    else:
                        logger.warning("New transformer tap position is NOT safe. (Note: Observed safe is also NOT safe)")
            else:
                logger.warning("New transformer tap position can not be evaluated due to missing or invalidated values.")
        elif switch:
            logger.warning("(Switch command)")
            if switch.calculateCommandEffects(calculatedState):
                logger.info("Observed state evaluation:")
                resultObserved = switch.connectedNode.executeSafetyCheck(observedValuesStore)
                observedSafety = resultObserved["R1"] and resultObserved["R4"] and resultObserved["R9a"] and resultObserved["R9b"]
                logger.info("Calculated state evaluation:")
                resultCalculated = switch.connectedNode.executeSafetyCheck(calculatedState)
                calculatedSafety = resultCalculated["R1"] and resultCalculated["R4"] and resultCalculated["R9a"] and resultCalculated["R9b"]
                logger.info("Safety before command (R1,R4,R9a,R9b): %s" % observedSafety)
                logger.info("Safety after command (R1,R4,R9a,R9b): %s" % calculatedSafety)
                if calculatedSafety:
                    logger.warning("New switch position is safe.")
                else:
                    if observedSafety:
                        logger.warning("New switch position is NOT safe.")
                    else:
                        logger.warning("New switch position is NOT safe. (Note: Observed safe is also NOT safe)")
            else:
                logger.warning("New switch position can not be evaluated due to missing or invalidated values.")
        else:
            logger.warning("(Unknown command (no set point, no transformer tap position, no switch command))")
    except Exception, e:
        logger.error("Unknown exception or error in command evaluation. %s" % e.message)


def invalidateStateValues(tagName, value, observedValuesStore):
    """
    Invalidates measurement values if there is a tap or switch position change
    :param tagName: Tag name of measured value
    :param value: Real process value with right type
    :param observedValuesStore: observed state object
    """
    try:
        VALUE_INVALIDATION_ALLOWED_AGE = 7
        if observedValuesStore.hasValue(tagName) and value <> observedValuesStore.retrieveValue(tagName, True):
            transformer = getTransformerByTag(tagName)
            switch = getSwitchByTag(tagName)
            if transformer:
                logger.debug("Transformer %s tap position changed. Invalidation:" % (transformer.name))
                for l in transformer.getAllConnectedLines():
                    currentTag = l.getLocalComponent(transformer, "local", "meter").currentKey
                    voltageTag = l.getLocalComponent(transformer, "local", "meter").voltageKey
                    if observedValuesStore.retrieveAge(currentTag) > VALUE_INVALIDATION_ALLOWED_AGE:
                        observedValuesStore.invalidateValue(currentTag)
                        logger.debug("Invalidate %s" % currentTag)
                    if observedValuesStore.retrieveAge(voltageTag) > VALUE_INVALIDATION_ALLOWED_AGE:
                        observedValuesStore.invalidateValue(voltageTag)
                        logger.debug("Invalidate %s" % voltageTag)

            elif switch:
                logger.debug("Switch %s position changed. Invalidation:" % (switch.name))
                for l in switch.connectedNode.getAllConnectedLines():
                    currentTag = l.getLocalComponent(switch.connectedNode, "local", "meter").currentKey
                    voltageTag = l.getLocalComponent(switch.connectedNode, "local", "meter").voltageKey
                    if observedValuesStore.retrieveAge(currentTag) > VALUE_INVALIDATION_ALLOWED_AGE:
                        observedValuesStore.invalidateValue(currentTag)
                        logger.debug("Invalidate %s" % currentTag)
                    if observedValuesStore.retrieveAge(voltageTag) > VALUE_INVALIDATION_ALLOWED_AGE:
                        observedValuesStore.invalidateValue(voltageTag)
                        logger.debug("Invalidate %s" % voltageTag)
    except Exception, e:
        logger.error("Unknown exception or error in measurement invalidation. %s" % e.message)


def processRecieved(timestamp, tagName, context, value):
    """
    Process a received measured or commanded value (independent of value type).
    :param timestamp: Timestamp of event
    :param tagName: Tag name of measured value
    :param context: "measured" or "commanded"
    :param value: Real process value with right type
    """
    global lock
    global scenario
    global observedValuesStore
    global lastValueUpdate
    global lastEvaluatedCommand
    global receivedCount
    COMMAND_EVALUATION = True
    with lock:
        receivedCount += 1
        if type(value) == float:
            logger.debug("[%s] [%s] Tag: %s, Value: %2.5f" % (context, formatTimestamp(timestamp), tagName, value))
        elif type(value) == bool:
            logger.debug("[%s] [%s] Tag: %s, Value: %s" % (context, formatTimestamp(timestamp), tagName, str(value)))
        else:
            logger.debug(
                "[%s] [%s] Tag: %s, Value: %s (unknown type)" % (context, formatTimestamp(timestamp), tagName, str(value)))
        if context == "measured":
            try:
                lastValueUpdate = time.time()
                if scenario == "Alpha" or scenario == "Masterthesis":
                    VALUE_INVALIDATION = False
                if VALUE_INVALIDATION:
                    invalidateStateValues(tagName, value, observedValuesStore)
                if scenario == "Alpha" or scenario == "Masterthesis":
                    observedValuesStore.updateValue(tagName, value)
                else:
                    assert False
            except Exception, e:
                logger.error("Unknown exception or error in receiving measurement. %s" % e.message)

        elif COMMAND_EVALUATION and context == "commanded":
            try:
                if lastEvaluatedCommand <> (tagName, value):
                    lastEvaluatedCommand = (tagName, value)
                    if scenario == "Alpha" or scenario == "Masterthesis":
                        evaluateCommand(tagName, value)
                    else:
                        assert False
            except Exception, e:
                logger.error("Unknown exception or error in receiving command. %s" % e.message)


def convertRaw(rawValue, rawType):
    """
    Convert a raw Bro value depending on type.
    :param rawValue: Raw Bro representation (bitarray interpreted as int)
    :param rawType: Type ("normalized", "double", "real", "doublePoint")
    :return: Converted real process value with right type
    """
    try:
        if rawType == "normalized":
            return normalize_value(rawValue)
        elif rawType == "double":
            return doublefy_value(rawValue)
        elif rawType == "real":
            return rawValue
        elif rawType == "doublePoint":
            return rawValue
        else:
            raise AssertionError("rawType not recognized. Valid values: normalized, double, real")
    except AssertionError, e:
        raise e
    except Exception, e:
        logger.error("Unknown exception or error in value conversion. %s" % e.message)
        return rawValue


@broccoli.event(broccoli.time, str, str, int, str)
def receiveTagRawValue(loggedNetworkTime, tagName, context, rawValue, rawType):
    """
    Bro is calling this function upon a measurement or command event of normalized/double value.

    :param loggedNetworkTime: Timestamp of event
    :param tagName: Tag name of measured value
    :param context: "measured" or "commanded"
    :param rawValue: Transmitted raw value (int as float representation)
    :param rawType: Type of raw format (e.g. "normalized", "double", "real", "doublePoint")
    """
    try:
        timestamp = int(loggedNetworkTime.val)
        measuredValue = convertRaw(rawValue, rawType)
        processRecieved(timestamp, tagName, context, measuredValue)
    except Exception, e:
        logger.error("Unknown exception or error in broccoli event receiveTagRawValue. %s" % e.message)


@broccoli.event(broccoli.time, str, str, bool)
def receiveTagSinglePoint(loggedNetworkTime, tagName, context, singlePoint):
    """
    Bro is calling this function upon a measurement or command event of single point values.

    :param loggedNetworkTime: Timestamp of event
    :param tagName: Tag name of measured value
    :param context: "measured" or "commanded"
    :param singlePoint: Transmitted single point value
    """
    try:
        timestamp = int(loggedNetworkTime.val)
        processRecieved(timestamp, tagName, context, singlePoint)
    except Exception, e:
        logger.error("Unknown exception or error in broccoli event receiveTagSinglePoint. %s" % e.message)


def printUsage():
    """Print the keyboard layout."""
    logger.warning("Starting Broccoli Main Loop.")
    logger.warning("Key bindings:")
    logger.warning("c: <C>lose/<Q>uit application (also q)")
    logger.warning("e: <E>valuate current state")
    logger.warning("a: Activate / deactivate <a>utomatic evaluation")
    logger.warning("v: Print current <v>alues")
    logger.warning("1: Set log level to <W>ARNING (also w)")
    logger.warning("2: Set log level to <I>NFO (also i)")
    logger.warning("3: Set log level to <D>EBUG (also d)")
    logger.warning("s: <S>ave values to file")
    logger.warning("l: <L>oad values from file")
    logger.warning("r: <r>esume session from last auto-save")


def startBroccoliMainLoop():
    """Start infinite event listener loop (infinite)."""
    global topology
    global observedValuesStore
    global lastValueUpdate
    printUsage()
    AUTOMATIC_EVALUATION_ENABLED = True
    AUTOMATIC_EVALUATION_INTERVAL = 3
    AUTOMATIC_EVALUATION_UPDATE_DELAY = 2
    AUTOMATIC_EVALUATION_UPDATE_DELAY_MAX = 10
    AUTOMATIC_SAVE_ENABLED = True
    AUTOMATIC_SAVE_INTERVAL = 10
    lastAutomaticEvaluation = time.time()
    lastAutomaticSave = time.time()
    lastValueUpdate = 0
    with KeyPoller() as keyPoller:
        while True:
            try:
                # Key handling
                c = keyPoller.poll()
                if not c is None:
                    if c == "c" or c == "q":
                        logger.warning("[Keyboard command] Closing application")
                        finishStateManager()
                    elif c == "e":
                        logger.warning("[Keyboard command] Evaluating current state")
                        checkTopology(topology, observedValuesStore)
                    elif c == "d" or c == "3":
                        logger.warning("[Keyboard command] Set log level to DEBUG")
                        logging.getLogger().setLevel(logging.DEBUG)
                    elif c == "i" or c == "2":
                        logger.warning("[Keyboard command] Set log level to INFO")
                        logging.getLogger().setLevel(logging.INFO)
                    elif c == "w" or c == "1":
                        logger.warning("[Keyboard command] Set log level to WARNING")
                        logging.getLogger().setLevel(logging.WARNING)
                    elif c == "v":
                        logger.warning("[Keyboard command] Print current values")
                        observedValuesStore.printCurrentState()
                    elif c == "s":
                        logger.warning("[Keyboard command] Save values to file")
                        try:
                            saveValuesToFile(observedValuesStore, autosave=False)
                        except Exception, e:
                            logger.warning("ERROR saving file: %s" % e)
                    elif c == "l":
                        logger.warning("[Keyboard command] Load values from file")
                        try:
                            observedValuesStore = loadValuesFromFile()
                        except Exception, e:
                            logger.warning("ERROR loading file: %s" % e)
                    elif c == "r":
                        logger.warning("[Keyboard command] Resuming last session from autosave file")
                        try:
                            observedValuesStore = loadValuesFromFile(loadAutosave=True)
                        except Exception, e:
                            logger.warning("ERROR loading file: %s" % e)
                    elif c == "a":
                        if AUTOMATIC_EVALUATION_ENABLED:
                            logger.warning("[Keyboard command] Automatic evaluation disabled")
                            AUTOMATIC_EVALUATION_ENABLED = False
                        else:
                            logger.warning("[Keyboard command] Automatic evaluation enabled")
                            AUTOMATIC_EVALUATION_ENABLED = True

                if AUTOMATIC_EVALUATION_ENABLED and lastAutomaticEvaluation < lastValueUpdate:
                    # Automatic Evaluation with update delay
                    if lastAutomaticEvaluation + AUTOMATIC_EVALUATION_INTERVAL < time.time() and lastValueUpdate + AUTOMATIC_EVALUATION_UPDATE_DELAY < time.time():
                        updateDescr = "(%ds Interval, %ds Update delay (max. %s)]" % (AUTOMATIC_EVALUATION_INTERVAL, AUTOMATIC_EVALUATION_UPDATE_DELAY, AUTOMATIC_EVALUATION_UPDATE_DELAY_MAX)
                        logger.warning("[Automatic Evaluation %s]" % updateDescr)
                        lastAutomaticEvaluation = time.time()
                        result = checkTopology(topology, observedValuesStore)
                        logger.warning("[Automatic Evaluation: Consistency: %s, Safety: %s]" % (str(result[0]), str(result[1])))

                    # Automatic Evaluation after update delay threshold
                    if lastAutomaticEvaluation + AUTOMATIC_EVALUATION_INTERVAL + AUTOMATIC_EVALUATION_UPDATE_DELAY_MAX < time.time():
                        logger.warning("[Automatic Evaluation (FORCED)]")
                        lastAutomaticEvaluation = time.time()
                        result = checkTopology(topology, observedValuesStore)
                        logger.warning("[Automatic Evaluation: Consistency: %s, Safety: %s]" % (str(result[0]), str(result[1])))

                if AUTOMATIC_SAVE_ENABLED and lastAutomaticSave < lastValueUpdate:
                    # Automatic save
                    if lastAutomaticSave + AUTOMATIC_SAVE_INTERVAL < time.time():
                        try:
                            logger.info("Automatically saving values to file.")
                            lastAutomaticSave = time.time()
                            saveValuesToFile(observedValuesStore, autosave=True)
                        except Exception, e:
                            logger.warning("ERROR saving file (auto-save): %s" % e)

                # Broccoli event handling
                global broccoliConnection
                broccoliConnection.processInput()

                # Sleep
                time.sleep(BROCCOLI_MAIN_LOOP_SLEEP)
            except KeyboardInterrupt:
                logger.warning("[Received Signal SIGINT] Closing application")
                finishStateManager()
            except Exception, e:
                logger.error("Unknown exception or error in broccoli main loop. %s" % e.message)


def initializeBroccoli():
    """Initialize connection to Bro."""
    failed = True
    while failed:
        try:
            global broccoliConnection
            broccoliConnection = broccoli.Connection(BROCCOLI_CONNECT)
            failed = False
            logger.info("Connected to Bro!")
        except Exception, e:
            logger.error("Unknown exception or error in broccoli initialization. %s" % e.message)


def initializeStateManager(topologyCreationFunction, currentScenario):
    """
    Initialize StateManager with a Brocooli connection and an empty value store.
    :param topologyCreationFunction: Function for topology creation
    :param currentScenario: Used underlaying scenario topology like "Masterthesis" or "Alpha"
    """
    initializeLogging(level=logging.INFO, logLevel=False, logLocation=False, logTime=True, logToFile=True)
    global scenario
    global topology
    global observedValuesStore
    scenario = currentScenario
    topology = topologyCreationFunction()
    observedValuesStore = ValueStore("T_{o}")
    initializeBroccoli()


def runStateManagerMainLoop():
    """Start state manager main loop."""
    startBroccoliMainLoop()


def finishStateManager():
    """Function that is called if StateManager is cancelled with SIGINT / CTRL + C."""
    global observedValuesStore
    observedValuesStore.printCurrentState()
    observedValuesStore.printFullHistory()
    global receivedCount
    logger.info("Total successfully received and parsed measurements and commands: %d" % receivedCount)
    sys.exit(0)
