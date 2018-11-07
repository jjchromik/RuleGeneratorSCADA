#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

from AbstractAPDU import AbstractAPDU


class APDUType03(AbstractAPDU):
    def __init__(self, commonAddress, infoObjectAddress, doublePointValue, dateTime=None):
        super(APDUType03, self).__init__(3, commonAddress, infoObjectAddress, dateTime)
        assert isinstance(doublePointValue, int)
        assert 0 <= doublePointValue and doublePointValue <= 3
        self.value = doublePointValue

    def toHex(self):
        return self.toHexDoublePointValue(qds=False, timetag=False)
