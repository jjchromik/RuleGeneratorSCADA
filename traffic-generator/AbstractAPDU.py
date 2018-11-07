#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
'''

import binascii
import datetime
import struct

from TrafficUtilities import datetime_to_cp56time2a, structToHex


class AbstractAPDU(object):
    def __init__(self, type, commonAddress, infoObjectAddress, dateTime=datetime.datetime(2000, 01, 01, 0, 0, 0)):
        assert isinstance(type, int) and type < 256
        assert isinstance(commonAddress, int) and commonAddress < 65536
        assert isinstance(infoObjectAddress, int) and infoObjectAddress < 16777216
        assert isinstance(dateTime, datetime.datetime)
        self.type = type
        self.ca = commonAddress
        self.ioa = infoObjectAddress
        self.dateTime = dateTime

    def hexType(self):
        return binascii.hexlify(struct.pack("B", self.type))

    def hexCa(self):
        return structToHex(struct.pack('BB', self.ca & 0xFF, self.ca >> 8 & 0xFF))

    def hexIoa(self):
        return structToHex(struct.pack('BBB', self.ioa & 0xFF, self.ioa >> 8 & 0xFF, self.ioa >> 16 & 0xFF))

    def hexDateTime(self):
        return datetime_to_cp56time2a(self.dateTime)

    def hexAPCI(self, asduLength, tx=3, rx=1):
        iec104MagicByte = "68"
        length = "%02x" % (asduLength / 2 + 4)
        tx = binascii.hexlify(struct.pack("H", tx * 2))
        rx = binascii.hexlify(struct.pack("H", rx * 2))
        return iec104MagicByte + length + tx + rx

    def hexTrailer(self):
        return self.hexType() + "013100" + self.hexCa() + self.hexIoa()

    def hexFooter(self, qds, timetag):
        tmp = ""
        if qds:
            tmp = tmp + "00"
        if timetag:
            tmp = tmp + self.hexDateTime()
        return tmp

    def toBytes(self):
        return self.toHex().decode('hex')

    def toHexSinglePointValue(self, qds, timetag):
        # Create ASDU
        hexValue = structToHex(struct.pack('B', self.value))
        asdu = self.hexTrailer() + hexValue + self.hexFooter(qds, timetag)
        # Create APCI + ASDU hex representation
        return self.hexAPCI(len(asdu)) + asdu

    def toHexDoublePointValue(self, qds, timetag):
        # Create ASDU
        hexValue = structToHex(struct.pack('B', self.value))
        asdu = self.hexTrailer() + hexValue + self.hexFooter(qds, timetag)
        # Create APCI + ASDU hex representation
        return self.hexAPCI(len(asdu)) + asdu

    def toHexNormalizedValue(self, qds, timetag):
        # Create ASDU
        hexValue = structToHex(struct.pack('<h', int(self.value * 32768)))
        asdu = self.hexTrailer() + hexValue + self.hexFooter(qds, timetag)
        # Create APCI + ASDU hex representation
        return self.hexAPCI(len(asdu)) + asdu

    def toHexFloatValue(self, qds, timetag):
        # Create ASDU
        hexValue = structToHex(struct.pack('f', self.value))
        asdu = self.hexTrailer() + hexValue + self.hexFooter(qds, timetag)
        # Create APCI + ASDU hex representation
        return self.hexAPCI(len(asdu)) + asdu

    def toHexC102(self):
        # Create ASDU
        asdu = self.hexTrailer()
        # Create APCI + ASDU hex representation
        return self.hexAPCI(len(asdu)) + asdu
