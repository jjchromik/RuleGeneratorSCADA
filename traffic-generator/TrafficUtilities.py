#!/usr/bin/python
# -*- coding: utf-8 -*-
'''


'''
import binascii
import datetime
import struct


def structToHex(packedStruct):
    return binascii.hexlify(packedStruct)


def hexToBytearray(hexlified):
    return bytearray.fromhex(hexlified)


def structToBytearray(packedStruct):
    return hexToBytearray(structToHex(packedStruct))


def datetime_to_cp56time2a(datetimeObject):
    ms = datetimeObject.microsecond // 1000 + datetimeObject.second * 1000
    minutes = datetimeObject.minute
    hours = datetimeObject.hour
    day = datetimeObject.day
    month = datetimeObject.month
    year = datetimeObject.year - 2000
    packedStruct = struct.pack('HBBBBB', ms, int((0 & 0b1) << 7 | (minutes & 0b111111)), int((0 & 0b1) << 7 | (hours & 0b11111)), int((0 & 0b111) << 5 | (day & 0b11111)), int(month & 0b1111), int(year & 0b1111111))
    return structToHex(packedStruct)


def cp56time2a_to_datetime(cp56time2aHex):
    cp56time2aBuffer = hexToBytearray(cp56time2aHex)
    microsecond = (cp56time2aBuffer[1] & 0xFF) << 8 | (cp56time2aBuffer[0] & 0xFF)
    microsecond %= 1000
    second = int(microsecond)
    minute = cp56time2aBuffer[2] & 0x3F
    hour = cp56time2aBuffer[3] & 0x1F
    day = cp56time2aBuffer[4] & 0x1F
    month = (cp56time2aBuffer[5] & 0x0F)
    year = (cp56time2aBuffer[6] & 0x7F) + 2000
    return datetime.datetime(year, month, day, hour, minute, second, microsecond)


def returnFormattedTime_cp56time2a(cp56time2aBuffer):
    return cp56time2a_to_datetime(cp56time2aBuffer).strftime("%Y-%m-%d_%H-%M-%S")


if __name__ == '__main__':
    print returnFormattedTime_cp56time2a("00002809020312")
    print returnFormattedTime_cp56time2a(datetime_to_cp56time2a(datetime.datetime(2018, 3, 2, 9, 40, 44)))
