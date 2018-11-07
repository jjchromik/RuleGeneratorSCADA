#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

from AbstractAPDU import AbstractAPDU


class APDUType102(AbstractAPDU):
    def __init__(self, commonAddress, infoObjectAddress):
        super(APDUType102, self).__init__(102, commonAddress, infoObjectAddress)

    def toHex(self):
        return self.toHexC102()
