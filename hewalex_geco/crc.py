# Based on work by krzysztof1111111111
# https://www.elektroda.pl/rtvforum/topic3499254.html


POLY = 0xD5
def crc8(buf):
    if len(buf) == 0:
        return 0

    accum = 0
    for i in buf:
        accum = accum ^ i
        for _ in range(8):
            if accum & 0x80:
                accum = (((accum << 1) & 0xff) ^ POLY) & 0xff
            else:
                accum = (accum << 1) & 0xff

    return accum

POLY16 = 0x1021
def crc16(buf):
    if len(buf) == 0:
        return 0

    accum = 0
    for i in buf:
        accum = accum ^ (i << 8)
        for _ in range(8):
            if accum & 0x8000:
                accum = (((accum << 1) & 0xffff) ^ POLY16) & 0xffff
            else:
                accum = (accum << 1) & 0xffff

    return accum
