#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This file offeres generalized test functions for scenario testing
'''
import logging
import os

from LoggerUtilities import logAllChecksDescription, logAllChecksPassed, logError
from ValueStore import ValueStore

logger = logging.getLogger(__name__)

SCENARIO_PATH = "../../state-manager/Scenarios/"


def playScenarios(caseName, topology, rtusToTest=None, filterFunction=lambda filename: True):
    """
    Load and test all or some cases of a scenario.
    :param caseName: Name of case
    :param topology: Topology list of RTUs
    :param rtusToTest: RTUs which should be tested
    :param filterFunction: Lambda filter function for filenames (e.g. for testing specific cases only)
    """
    scenarioFiles = []
    basicCaseFilename = "%s_%s.state" % (caseName, "BasicCase")
    basicCaseFound = False
    for filename in os.listdir(SCENARIO_PATH):
        if filename == basicCaseFilename:
            basicCaseFound = True
        else:
            if filename.startswith(caseName) and filename.endswith(".state"):
                scenarioFiles.append(filename)
    assert basicCaseFound
    logger.warn("Testing %d scenarios of case %s." % (len(filter(filterFunction, sorted(scenarioFiles))), caseName))
    for scenarioFilename in filter(filterFunction, sorted(scenarioFiles)):
        stateScenario = ValueStore("T_{o}")
        stateScenario.loadFromFile("%s%s" % (SCENARIO_PATH, basicCaseFilename))
        stateScenario.loadFromFile("%s%s" % (SCENARIO_PATH, scenarioFilename))
        logger.warn("")
        logger.warn(stateScenario.description)
        checkTopology(topology, stateScenario, rtusToTest)


def checkTopology(topology, state, rtusToTest=None):
    """
    Evaluate all consistency and safety rules on the topology with the given state information
    :param topology: Topology list of RTUs
    :param state: State object with stateful information
    :param rtusToTest: RTUs which should be tested
    :return: (T,T) If all tests are successful, (F,T) if consistency violation, (T,F) if safety violation, (F,F) if violation in both
    """
    logAllChecksDescription("ALL CHECKS", "TOPOLOGY", indentation=0)
    checkStatusConsistency = dict()
    checkStatusSafety = dict()
    try:
        if type(rtusToTest) == set or type(rtusToTest) == list:
            relevantRTUs = [rtu for rtu in topology if rtu.name in rtusToTest]
        else:
            relevantRTUs = topology
        for rtu in relevantRTUs:
            checkStatusConsistency[rtu.name] = all(rtu.executeFullConsistencyCheck(state).values())
            checkStatusSafety[rtu.name] = all(rtu.executeFullSafetyCheck(state).values())
        logAllChecksPassed("ALL CHECKS", "TOPOLOGY", all(checkStatusConsistency.values()) and all(checkStatusSafety.values()), indentation=0)
    except Exception, e:
        logError("Unknown exception or error: %s" % e.message, indentation=0)
    return (all(checkStatusConsistency.values()), all(checkStatusSafety.values()))


def generateRules(topology):
    """
    Start the Bro rule generation process.
    :param topology: Topology list of RTUs
    """
    for rtu in topology:
        rtu.generateFullBroConsistencyCheck()
        rtu.generateFullBroSafetyCheck()
