from binascii import hexlify, unhexlify

from ..crc import *

# Based on work by krzysztof1111111111
# https://www.elektroda.pl/rtvforum/topic3499254.html


class PCWU:
    def __init__(self, conHardId, conSoftId, devHardId, devSoftId, onMessage=None):
        self.conHardId = conHardId  # G-426 controller - physical address
        self.conSoftId = conSoftId  # G-426 controller - logical address
        self.devHardId = devHardId  # PCWU device - physical address
        self.devSoftId = devSoftId  # PCWU device - logical address
        self.onMessage = onMessage  # Callback - onMessage(obj, h, sh, m)

    def parseHardHeader(self, m):
        if len(m) < 8:
            raise Exception("Too short message")
        calcCrc = crc8(m[:7])
        return {
            "StartByte": m[0],
            "To": m[1],
            "From": m[2],
            "ConstBytes": (m[5] << 16) | (m[4] << 8) | m[3],
            "Payload": m[6],
            "CRC8": m[7],
            "CalcCRC8": calcCrc
        }

    def validateHardHeader(self, h):
        if h["StartByte"] != 0x69:
            raise Exception("Invalid Start Byte")
        if h["CRC8"] != h["CalcCRC8"]:
            raise Exception("Invalid Hard CRC8")
        if h["ConstBytes"] != 0x84:
            raise Exception("Invalid Const Bytes")
        if h["From"] != self.conHardId and h["From"] != self.devHardId:
            raise Exception("Invalid From Hard Address: " + str(h["From"]))
        if h["To"] != self.conHardId and h["To"] != self.devHardId:
            raise Exception("Invalid To Hard Address: " + str(h["To"]))
        if h["To"] == h["From"]:
            raise Exception("From and To Hard Address Equal")

    def getWord(self, w):
        return (w[1] << 8) | w[0]

    def getWordReverse(self, w):
        return (w[0] << 8) | w[1]

    def parseSoftHeader(self, h, m):
        if len(m) != h["Payload"]:
            raise Exception("Invalid soft message len")
        if len(m) < 12:
            raise Exception("Too short soft message")
        calcCrc = crc16(m[:h["Payload"]-2])
        return {
            "To": self.getWord(m[0:]),
            "From": self.getWord(m[2:]),
            "FNC": m[4],
            "ConstByte": self.getWord(m[5:]),
            "RegLen": m[7],
            "RegStart": self.getWord(m[8:]),
            "RestMessage": m[10:h["Payload"]-2],
            "CRC16": self.getWordReverse(m[h["Payload"]-2:]),
            "CalcCRC16": calcCrc
        }

    def validateSoftHeader(self, h, sh):
        if sh["CRC16"] != sh["CalcCRC16"]:
            raise Exception("Invalid Soft CRC16")
        if sh["ConstByte"] != 0x80:
            raise Exception("Invalid Const Soft Byte 0x80")
        if (h["From"] == self.conHardId and sh["From"] != self.conSoftId) or (h["From"] == self.devHardId and sh["From"] != self.devSoftId):
            raise Exception("Invalid From Address")
        if (h["To"] == self.conHardId and sh["To"] != self.conSoftId) or (h["To"] == self.devHardId and sh["To"] != self.devSoftId):
            raise Exception("Invalid To Address")

    def getTemp(self, w):
        w = self.getWord(w)
        if w & 0x8000:
            w = w - 0x10000
        return w / 10.0

    def parseRegisters(self, m):
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

        ret["date"] = "20{:02d}-{:02d}-{:02d}".format(m[0], m[1], m[2]) #m[3] Day Of Week 0 = Monday
        ret["time"] = "{:02d}:{:02d}:{:02d}".format(m[4], m[5], m[6]) #m[7] always 0, probably for proper aligment

        ret["unknown5"] = hex(self.getWord(m[46:]))
        ret["unknown3"] = hex(self.getWord(m[72:])) #org 73
        ret["IsManual"] = self.getWord(m[74:])
        ret["unknown1"] = hex(self.getWord(m[76:]))
        ret["EV1"] = self.getWord(m[78:]) #unknown4
        ret["unknown2"] = hex(m[82])
        ret["unknown6"] = hex(self.getWord(m[86:]))
        ret["unknown7"] = hex(self.getWord(m[90:]))
        if len(m) == 104:
            ret["unknown8"] = hex(self.getWord(m[98:]))
            ret["unknown9"] = hex(self.getWord(m[100:]))
        for name in temp:
            ret[name] = self.getTemp(m[temp[name]:])
        return ret

    def printMessage(self, h, sh):
        print ({
            'hard': {
                "StartByte": hex(h["StartByte"]),
                "To": h["To"],
                "From": h["From"],
                "ConstBytes": hex(h["ConstBytes"]),
                "Payload": h["Payload"],
                "CRC8": hex(h["CRC8"])
            },
            'soft': {
                "To": sh["To"],
                "From": sh["From"],
                "FNC": hex(sh["FNC"]),
                "ConstByte": hex(sh["ConstByte"]),
                "RegLen": sh["RegLen"],
                "RegStart": str(sh["RegStart"]) + " (" + hex(sh["RegStart"]) + ")",
                "RestMessage": hexlify(sh["RestMessage"]),
                "CRC16": hex(sh["CRC16"])
            }
        })

    def processMessage(self, m, ignoreTooShort):
        h = self.parseHardHeader(m)
        self.validateHardHeader(h)
        ml = h["Payload"]
        if ignoreTooShort and ml + 8 > len(m):
            return m
        sh = self.parseSoftHeader(h, m[8:ml+8])
        self.validateSoftHeader(h, sh)
        if self.onMessage:
            self.onMessage(self, h, sh, m)
        return m[ml+8:]

    def processAllMessages(self, m, returnRemainingBytes=False):
        minLen = 8 if returnRemainingBytes else 0
        prevLen = len(m)
        while prevLen > minLen:
            m = self.processMessage(m, returnRemainingBytes)
            if len(m) == prevLen:
                if returnRemainingBytes:
                    return m
                else:
                    raise Exception("Something wrong")
            prevLen = len(m)
        return m

    # Process all messages in X cycles of device to controller comms
    #
    # 1. The pump sends a query to the display to read 20 registers starting from address 100.
    # 2. The display responds, it always seems to be the same. It's hard to say if there is a display model or a serial number.
    # 3. The pump sends a record of 92 or 104 registers starting at address 120. This is the main message, there are temperatures there. After this message there is a long pause (which is quite a large part of the 140ms for a series of messages), probably the display is not too fast to write it to memory and it takes longer. The exact number of records depends on the model and firmware of the pump.
    # 4. The display replies with the standard message 0x70 that the bytes have been written successfully.
    # 5. The pump requests to read 4 bytes starting from address 252.
    # 6. The display responds and returns 4 bytes. By default they are: 10000000 and they mean that the display is working normally, there are no changes. The value 08000000 means that the display is turned off. However, the value 11000000 means that the user has changed a parameter in the menu, at this point the communication scheme is different, described below.
    #
    def eavesDrop(self, ser, numCycles=None):
        # window size and time (based on 140ms cycle and 360ms wait)
        winSize = 1000
        winTime = 0.4

        # determine start of cycle marker to look for
        # (device requesting to read 20 registers from address 100)
        s1 = unhexlify('69%02x%02x8400000c' % (self.devHardId, self.conHardId))
        s2 = unhexlify('%02x' % crc8(s1))
        s3 = unhexlify('%02x%02x%02x%02x' % (
            (self.devSoftId & 0xff),
            (self.devSoftId & 0xff00) >> 8,
            (self.conSoftId & 0xff),
            (self.conSoftId & 0xff00) >> 8,
        ))
        s4 = unhexlify('408000146400')
        s = s1 + s2 + s3 + s4

        ser.flushInput()
        cnt = 0
        while (numCycles is None) or (cnt < numCycles):
            cnt += 1

            # read until first char after start marker
            ser.timeout = 1
            m = ser.read_until(s, winSize)

            # read the rest within window
            ser.timeout = winTime
            m = ser.read(winSize)

            # process
            self.processAllMessages(s + m)

    def createRegistersRequest(self, SlaveHardId, MasterHardId, SlaveSoftId, MasterSoftId, num, start):
        header = [0x69, SlaveHardId, MasterHardId, 0x84, 0, 0]
        payload = [(SlaveSoftId & 0xff), ((SlaveSoftId >> 8) & 0xff), (MasterSoftId & 0xff), ((MasterSoftId >> 8) & 0xff), 0x40, 0x80, 0, num, start, 0]
        calcCrc16 = crc16(payload)
        payload.append((calcCrc16 >> 8) & 0xff)
        payload.append(calcCrc16 & 0xff)
        header.append(len(payload))
        calcCrc8 = crc8(header)
        header.append(calcCrc8)
        return bytearray(header + payload)

    def requestRegisters(self, ser, num, start):
        m = self.createRegistersRequest(self.devHardId, self.conHardId, self.devSoftId, self.conSoftId, num, start)
        ser.flushInput()
        ser.timeout = 0.4
        ser.write(m)
        r = ser.read(1000)
        self.processAllMessages(r)
