#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This file starts the Interlock tests directly from the scenario files (without traffic).
Only for testing and model verification purposes while developing.
Important for regression tests.
'''
import logging
import time

from LoggerUtilities import initializeLogging
from TestTopologies import initiateTopologyInterlock
from TestUtilities import playScenarios

logger = logging.getLogger(__name__)


def runInterlock():
    """Start Interlock with all scenario cases."""
    playScenarios(caseName="Interlock", topology=initiateTopologyInterlock(), rtusToTest={"rtu1"})


if __name__ == '__main__':
    initializeLogging(level=logging.INFO, logLevel=False, logLocation=False, logTime=False)
    start = time.time()
    runInterlock()
    end = time.time()
    logger.info("All tests completed in %2.3fs." % (end - start))
