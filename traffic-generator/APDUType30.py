#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

import datetime

from AbstractAPDU import AbstractAPDU


class APDUType30(AbstractAPDU):
    def __init__(self, commonAddress, infoObjectAddress, boolValue, dateTime=datetime.datetime(2000, 01, 01, 0, 0, 0)):
        super(APDUType30, self).__init__(30, commonAddress, infoObjectAddress, dateTime)
        assert isinstance(boolValue, bool)
        self.value = boolValue

    def toHex(self):
        return self.toHexSinglePointValue(qds=False, timetag=True)
