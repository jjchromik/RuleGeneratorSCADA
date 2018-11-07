#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This file starts the TransfFuseRelayGlobal tests directly from the scenario files (without traffic).
Only for testing and model verification purposes while developing.
Important for regression tests.
'''
import logging
import time

from LoggerUtilities import initializeLogging
from TestTopologies import initiateTopologyTransfFuseRelay
from TestUtilities import playScenarios

logger = logging.getLogger(__name__)


def runTransfFuseRelayGlobal():
    """Start TransfFuseRelayGlobal with all scenario cases."""
    playScenarios(caseName="TransfFuseRelay", topology=initiateTopologyTransfFuseRelay())


def runTransfFuseRelayGlobalOnly3():
    """Start TransfFuseRelayGlobal with scenario case 3."""
    playScenarios(caseName="TransfFuseRelay", topology=initiateTopologyTransfFuseRelay(), rtusToTest={"rtu1"}, filterFunction=lambda filename: "Scenario3" in filename)


if __name__ == '__main__':
    initializeLogging(level=logging.INFO, logLevel=False, logLocation=False, logTime=False)
    start = time.time()
    runTransfFuseRelayGlobal()
    runTransfFuseRelayGlobalOnly3()
    end = time.time()
    logger.info("All tests completed in %2.3fs." % (end - start))
