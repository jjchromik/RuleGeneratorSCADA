#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This file contains all utilities for convenient logging of the intrusion detection rule evaluation
'''
import logging
import time

from StateManagerUtilities import formatTimestamp

logger = logging.getLogger(__name__)

CHECK_DESCRIPTIONS = {"P1": "Kirchoff's current law holds. (local)",
                      "P2": "All voltage values equal. (local)",
                      "P3": "Switch/Fuse/Protective Relay open -> no current. (local, semi-global)",
                      "P4": "Current and voltage equal at beginning and end of line. (semi-global)",
                      "P5a": "Generator: V*I=P holds. (local)",
                      "P5b": "Consumer: V*I=P holds. (local)",
                      "P6a": "Transformer transformation rate is consistent in voltage. (local)",
                      "P6b": "Transformer transformation rate is consistent in current. (local)",
                      "P7": "Transformer has transformation rate defined. (local)",
                      "R1": "Current does not exceed maximum of power line. (local)",
                      "R2": "Nominal voltage boundary of power line is obeyed. (local)",
                      "R3": "No fuse is molten / protective relay is open. (local)",
                      "R4": "No fuse / protective relay has current above cutting current. (local)",
                      "R5a": "Transformer transformation rate is safe on nominal voltage. (local)",
                      "R5b": "Transformer transformation rate is safe on actual voltage. (local)",
                      "R6": "All consumers are connected to a power supply. (local)",
                      "R7": "Produced power equals consumed power. (global)",
                      "R8a": "Voltage set points are safe (local)",
                      "R8b": "Current set points are safe (local)",
                      "R9a": "Static interlocks are ensured. (local)",
                      "R9b": "Dynamic interlocks are ensured. (local)"}


def logDebugCheckValues(message, passed, indentation=0):
    """
    Log messages about values in rule evaluation.
    :param message: Message to log
    :param passed: Test successful (True) or violation (False)
    :param indentation: Indentation level
    """
    indentation += 1
    if passed:
        logger.debug("%s%s (%s)" % ("\t" * indentation, message, str(passed)))
    else:
        if logger.getEffectiveLevel() == logging.WARNING:
            logger.warn("%s (%s)" % (message, str(passed)))
        else:
            logger.info("%s%s (%s)" % ("\t" * indentation, message, str(passed)))


def logDebugUnknownValues(exceptionMessage, component=None, indentation=0):
    """
    Log messages about missing values in rule evaluation.
    :param exceptionMessage: Exception message with tag
    :param component: Location of missing value
    :param indentation: Indentation level
    """
    indentation += 1
    if component:
        logger.debug("%sProper check is not possible (at %s). At least one value is unknown: %s (True)" % ("\t" * indentation, component, exceptionMessage))
    else:
        logger.debug("%sProper check is not possible. At least one value is unknown: %s (True)" % ("\t" * indentation, exceptionMessage))


def logCheckDescription(testName, indentation=0):
    """
    Log rule description at beginning of evaluation.
    :param testName: Name of test
    :param indentation: Indentation level
    """
    logger.debug("%sChecking %s: %s" % ("\t" * indentation, testName, CHECK_DESCRIPTIONS[testName]))


def logCheckPassed(testName, passed, indentation=0):
    """
    Log rule description and test result at end of evaluation.
    :param testName: Name of test
    :param passed: Test successful (True) or violation (False)
    :param indentation: Indentation level
    """
    if passed:
        logger.info("%s[x] %s: %s" % ("\t" * indentation, testName, CHECK_DESCRIPTIONS[testName]))
    else:
        logger.info("%s[ ] %s: %s" % ("\t" * indentation, testName, CHECK_DESCRIPTIONS[testName]))


def logAllChecksDescription(description, nodeName, indentation=0):
    """
    Log evaluation start at beginning of new node.
    :param description: Test type "CONSISTENCY" or "SAFETY"
    :param nodeName: Name of node
    :param indentation: Indentation Level
    """
    if indentation == 1:
        logger.info("")
    logger.info("%sChecking %s %s" % ("\t" * indentation, description, nodeName))


def logAllChecksPassed(description, nodeName, passed, indentation=0):
    """
    Log evaluation results at end of node evaluation.
    :param description: Test type "CONSISTENCY" or "SAFETY"
    :param nodeName: Name of node
    :param passed: All tests successful (True) or at least one violation (False)
    :param indentation: Indentation Level
    """
    if passed:
        logger.info("%s[x] %s %s" % ("\t" * indentation, description, nodeName))
    else:
        logger.info("%s[ ] %s %s" % ("\t" * indentation, description, nodeName))


def logError(message, indentation):
    """
    Log an error in the evaluation process
    :param message: Exception message
    :param indentation: Indentation Level
    """
    logger.error("%sEXCEPTION: %s" % ("\t" * indentation, message))


def initializeLogging(level=logging.INFO, logLevel=True, logLocation=False, logTime=True, logToFile=True):
    """
    Initialize the general logging settings
    :param level: Log level (logging.INFO or logging.DEBUG)
    :param logLevel: Print log level if True
    :param logLocation: Print location of log if True
    :param logTime: Print time if True
    """
    if logToFile:
        fileHandler = logging.FileHandler(filename='/tmp/StateManager_%s.log' % formatTimestamp(time.time(), fileFormat=True))
        for k, v in logging.Logger.manager.loggerDict.iteritems():
            v.addHandler(fileHandler)
    format = "%(message)s"
    if logLevel:
        format = "%(levelname)s " + format
    if logTime:
        format = "[%(asctime)s] " + format
    if logLocation:
        format = format + " [Location: %(module)s:%(lineno)s]"
    logging.basicConfig(format=format, level=level)
