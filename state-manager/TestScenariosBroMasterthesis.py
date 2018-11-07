#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This script starts the python broccoli interface and state manager to work with Bro on Alpha_GlobalKnowledge and Alpha_LocalKnowledge.
'''

import StateManager
from TestTopologies import initiateTopologyMasterthesis

if __name__ == '__main__':
    StateManager.initializeStateManager(initiateTopologyMasterthesis, "Masterthesis")
    StateManager.runStateManagerMainLoop()
