#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

from AbstractAPDU import AbstractAPDU


class APDUType09(AbstractAPDU):
    def __init__(self, commonAddress, infoObjectAddress, floatValue, dateTime=None):
        super(APDUType09, self).__init__(9, commonAddress, infoObjectAddress, dateTime)
        if isinstance(floatValue, int):
            floatValue = float(floatValue)
        assert isinstance(floatValue, float)
        self.value = floatValue

    def toHex(self):
        return self.toHexNormalizedValue(qds=True, timetag=False)
