#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

from AbstractAPDU import AbstractAPDU


class APDUType59(AbstractAPDU):
    def __init__(self, commonAddress, infoObjectAddress, doublePointValue, dateTime=None):
        super(APDUType59, self).__init__(59, commonAddress, infoObjectAddress, dateTime)
        assert isinstance(doublePointValue, int)
        assert 0 <= doublePointValue and doublePointValue <= 3
        self.value = doublePointValue

    def toHex(self):
        return self.toHexDoublePointValue(qds=False, timetag=True)
