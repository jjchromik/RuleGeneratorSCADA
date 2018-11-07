#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

import datetime

from AbstractAPDU import AbstractAPDU


class APDUType36(AbstractAPDU):
    def __init__(self, commonAddress, infoObjectAddress, floatValue, dateTime=datetime.datetime(2000, 01, 01, 0, 0, 0)):
        super(APDUType36, self).__init__(36, commonAddress, infoObjectAddress, dateTime)
        if isinstance(floatValue, int):
            floatValue = float(floatValue)
        assert isinstance(floatValue, float)
        self.value = floatValue

    def toHex(self):
        return self.toHexFloatValue(qds=True, timetag=True)
