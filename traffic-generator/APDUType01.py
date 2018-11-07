#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''

from AbstractAPDU import AbstractAPDU


class APDUType01(AbstractAPDU):
    def __init__(self, commonAddress, infoObjectAddress, boolValue, dateTime=None):
        super(APDUType01, self).__init__(1, commonAddress, infoObjectAddress, dateTime)
        assert isinstance(boolValue, bool)
        self.value = boolValue

    def toHex(self):
        return self.toHexSinglePointValue(qds=False, timetag=False)
