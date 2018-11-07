#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents an abstract protective device.
'''
from GridComponents.AbstractDecorator import AbstractDecorator


class AbstractProtectiveDevice(AbstractDecorator):
    def __init__(self, name, cuttingI, cuttingT=0, stateKey=None):
        """
        Initialize a fuse.
        :param name: Name of the transformer.
        :param cuttingI: Cutting current
        :param cuttingT: Cutting time
        :param stateKey: Key for retrieving circuit state
        """
        super(AbstractProtectiveDevice, self).__init__(name)
        assert cuttingI
        self.cuttingI = cuttingI
        self.cuttingT = cuttingT
        self.stateKey = stateKey if stateKey else "%s_STATE" % self.name.upper()
