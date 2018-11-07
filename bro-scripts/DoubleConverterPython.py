#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

This script takes an hexadecimal float and converts it to hexadecimal double.
'''

import struct
import sys

if __name__ == '__main__':
    assert len(sys.argv)==2
    print struct.unpack('!f', ("%x" % int(sys.argv[1])).decode('hex'))[0]