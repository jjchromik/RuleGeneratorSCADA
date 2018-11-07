#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This class represents a fuse.
'''
from GridComponents.AbstractProtectiveDevice import AbstractProtectiveDevice


class Fuse(AbstractProtectiveDevice):
    def __init__(self, name, cuttingI, cuttingT=0, stateKey=None):
        """
        Initialize a fuse.
        :param name: Name of the transformer.
        :param cuttingI: Cutting current
        :param cuttingT: Cutting time
        :param stateKey: Key for retrieving circuit state
        """
        super(Fuse, self).__init__(name, cuttingI, cuttingT, stateKey)
