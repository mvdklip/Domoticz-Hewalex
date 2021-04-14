from binascii import hexlify, unhexlify

from .base import BaseDevice
from ..crc import *

# Based on work by aelias-eu
# https://github.com/aelias-eu/hewalex-geco-protocol


class ZPS(BaseDevice):
    def parseStatusRegisters(self, m):
        temp = {
            'T1': 8,
            'T2': 10,
            'T3': 12,
            'T4': 14,#
            'T5': 16,#
            'T6': 18,
        }
        ret = {}

        ret["date"] = "20{:02d}-{:02d}-{:02d}".format(m[0], m[1], m[2]) #m[3] Day Of Week 0 = Monday
        ret["time"] = "{:02d}:{:02d}:{:02d}".format(m[4], m[5], m[6]) #m[7] always 0, probably for proper aligment

        for name in temp:
            ret[name] = self.getTemp(m[temp[name]:], 1)

        ret["SolarPower"] = self.getWord(m[24:])                # Watt
        ret["Reg148"] = self.getWord(m[28:])
        ret["CollectorPumpON"] = self.getWord(m[30:])
        ret["Flow"] = self.getWord(m[32:]) / 10.0               # l/min
        ret["Reg154"] = self.getWord(m[34:])
        ret["Reg156"] = self.getWord(m[36:])
        ret["TotalEnergy"] = self.getWord(m[46:]) / 10.0        # kWh

        return ret

    def readStatusRegisters(self, ser):
        return self.readRegisters(ser, 120, 50)

#    def disable(self, ser):
#        return self.writeRegister(ser, X, 0)

#    def enable(self, ser):
#        return self.writeRegister(ser, X, 1)
