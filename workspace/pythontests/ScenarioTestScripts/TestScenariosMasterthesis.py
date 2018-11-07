#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This file starts the Masterthesis tests directly from the scenario files (without traffic).
Only for testing and model verification purposes while developing.
Important for regression tests.
'''
import logging
import time

from LoggerUtilities import initializeLogging
from TestTopologies import initiateTopologyAlpha
from TestUtilities import playScenarios

logger = logging.getLogger(__name__)


def runAlphaGlobalOnly1():
    """Start Alpha_GlobalKnowledge with scenario case 1."""
    playScenarios(caseName="Masterthesis_GlobalKnowledge", topology=initiateTopologyAlpha(), filterFunction=lambda filename: "Scenario1" in filename)


if __name__ == '__main__':
    initializeLogging(level=logging.INFO, logLevel=False, logLocation=False, logTime=False)
    start = time.time()
    runAlphaGlobalOnly1()
    end = time.time()
    logger.info("All tests completed in %2.3fs." % (end - start))
