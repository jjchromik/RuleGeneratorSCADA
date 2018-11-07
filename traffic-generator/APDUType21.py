#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

from AbstractAPDU import AbstractAPDU


class APDUType21(AbstractAPDU):
    def __init__(self, commonAddress, infoObjectAddress, floatValue, dateTime=None):
        super(APDUType21, self).__init__(21, commonAddress, infoObjectAddress, dateTime)
        if isinstance(floatValue, int):
            floatValue = float(floatValue)
        assert isinstance(floatValue, float)
        self.value = floatValue

    def toHex(self):
        return self.toHexNormalizedValue(qds=False, timetag=False)
