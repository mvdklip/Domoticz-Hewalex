from binascii import hexlify, unhexlify

from .base import BaseDevice
from ..crc import *

# Based on work by krzysztof1111111111
# https://www.elektroda.pl/rtvforum/topic3499254.html


class PCWU(BaseDevice):
    def parseStatusRegisters(self, m):
        temp = {
            'T1': 8,
            'T2': 10,
            'T3': 12,
            'T4': 14,#
            'T5': 16,#
            'T6': 18,
            'T7': 20,
            'T8': 22,
            'T9': 24,
            'T10': 26
        }
        ret = {}

        if len(m) >= 92:
            ret["date"] = "20{:02d}-{:02d}-{:02d}".format(m[0], m[1], m[2]) #m[3] Day Of Week 0 = Monday
            ret["time"] = "{:02d}:{:02d}:{:02d}".format(m[4], m[5], m[6]) #m[7] always 0, probably for proper aligment

            for name in temp:
                ret[name] = self.getTemp(m[temp[name]:], 10.0)

            ret["unknown5"] = hex(self.getWord(m[46:]))
            ret["unknown3"] = hex(self.getWord(m[72:])) #org 73
            ret["IsManual"] = self.getWord(m[74:])
            ret["unknown1"] = hex(self.getWord(m[76:]))
            ret["EV1"] = self.getWord(m[78:]) #unknown4
            ret["WaitingStatus"] = self.getWord(m[82:])
            ret["unknown6"] = hex(self.getWord(m[86:]))
            ret["unknown7"] = hex(self.getWord(m[90:]))

            if len(m) >= 104:
                ret["unknown8"] = hex(self.getWord(m[98:]))
                ret["unknown9"] = hex(self.getWord(m[100:]))

        return ret

    def readStatusRegisters(self, ser):
        return self.readRegisters(ser, 120, 92)     # TODO - find out why some heat pumps do 92 and others do 104 registers

    def disable(self, ser):
        return self.writeRegister(ser, 304, 0)

    def enable(self, ser):
        return self.writeRegister(ser, 304, 1)
