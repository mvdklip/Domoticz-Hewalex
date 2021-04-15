from .base import BaseDevice

# Based on work by krzysztof1111111111
# https://www.elektroda.pl/rtvforum/topic3499254.html


class PCWU(BaseDevice):
    registers = {
        120: { 'type': 'date', 'name': 'date' },                        # Date
        124: { 'type': 'time', 'name': 'time' },                        # Time
        128: { 'type': 'te10', 'name': 'T1' },                          # T1 (Ambient temp)
        130: { 'type': 'te10', 'name': 'T2' },                          # T2 (Tank bottom temp)
        132: { 'type': 'te10', 'name': 'T3' },                          # T3 (Tank top temp)
        138: { 'type': 'te10', 'name': 'T6' },
        140: { 'type': 'te10', 'name': 'T7' },
        142: { 'type': 'te10', 'name': 'T8' },
        144: { 'type': 'te10', 'name': 'T9' },
        146: { 'type': 'te10', 'name': 'T10' },
        194: { 'type': 'bool', 'name': 'IsManual' },
        198: { 'type': 'word', 'name': 'EV1' },
        202: { 'type': 'word', 'name': 'WaitingStatus' },
    }

    def readStatusRegisters(self, ser):
        # registers below 256 (dubbed 'status registers') are read-only
        # the most interesting registers start at 120
        # in eavesdropping mode some pumps send 92 registers, others send 104; why is unknown
        return self.readRegisters(ser, 120, 92)

    def disable(self, ser):
        return self.writeRegister(ser, 304, 0)

    def enable(self, ser):
        return self.writeRegister(ser, 304, 1)
