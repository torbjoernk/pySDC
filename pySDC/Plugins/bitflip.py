__author__ = 'robert'

import struct

def __bitsToFloat(b):
    s = struct.pack('>l', b)
    return struct.unpack('>f', s)[0]

def __floatToBits(f):
    s = struct.pack('>f', f)
    return struct.unpack('>l', s)[0]

def do_bitflip(a,pos=29):

    b = __floatToBits(a)
    mask = 1<<pos
    c = b^mask

    return __bitsToFloat(c)