#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

import datetime

from AbstractAPDU import AbstractAPDU


class APDUType31(AbstractAPDU):
    def __init__(self, commonAddress, infoObjectAddress, doublePointValue, dateTime=datetime.datetime(2000, 01, 01, 0, 0, 0)):
        super(APDUType31, self).__init__(31, commonAddress, infoObjectAddress, dateTime)
        assert isinstance(doublePointValue, int)
        assert 0 <= doublePointValue and doublePointValue <= 3
        self.value = doublePointValue

    def toHex(self):
        return self.toHexDoublePointValue(qds=False, timetag=True)
