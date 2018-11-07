#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents a protective relay.
'''
from GridComponents.AbstractProtectiveDevice import AbstractProtectiveDevice


class ProtectiveRelay(AbstractProtectiveDevice):
    def __init__(self, name, cuttingI, cuttingT=0, stateKey=None):
        """
        Initialize a protective relay.
        :param name: Name of the protective relay.
        :param cuttingI: Cutting current
        :param cuttingT: Cutting time
        :param stateKey: Key for retrieving circuit state
        """
        super(ProtectiveRelay, self).__init__(name, cuttingI, cuttingT, stateKey)
