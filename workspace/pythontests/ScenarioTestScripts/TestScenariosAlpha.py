#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This file starts the Alpha_GlobalKnowledge or Alpha_LocalKnowledge tests directly from the scenario files (without traffic).
Only for testing and model verification purposes while developing.
Important for regression tests.
'''
import logging
import time

from LoggerUtilities import initializeLogging
from TestTopologies import initiateTopologyAlpha
from TestUtilities import playScenarios

logger = logging.getLogger(__name__)


def runAlphaGlobal():
    """Start Alpha_GlobalKnowledge with all scenario cases."""
    playScenarios(caseName="Alpha_GlobalKnowledge", topology=initiateTopologyAlpha())


def runAlphaLocal():
    """Start Alpha_LocalKnowledge with all scenario cases on rtu1."""
    playScenarios(caseName="Alpha_LocalKnowledge", topology=initiateTopologyAlpha(), rtusToTest={"rtu1"})


def runAlphaGlobalOnly1():
    """Start Alpha_GlobalKnowledge with scenario case 1."""
    playScenarios(caseName="Alpha_GlobalKnowledge", topology=initiateTopologyAlpha(), filterFunction=lambda filename: "Scenario1" in filename)


if __name__ == '__main__':
    initializeLogging(level=logging.INFO, logLevel=False, logLocation=False, logTime=False)
    start = time.time()
    runAlphaGlobal()
    runAlphaLocal()
    runAlphaGlobalOnly1()
    end = time.time()
    logger.info("All tests completed in %2.3fs." % (end - start))
