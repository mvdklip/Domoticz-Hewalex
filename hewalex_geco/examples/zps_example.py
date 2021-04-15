import serial


# ZPS communication example
from hewalex_geco.devices import ZPS

# Controller (Master)
conHardId = 1
conSoftId = 1

# ZPS (Slave)
devHardId = 2
devSoftId = 2

# onMessage handler
def onMessage(obj, h, sh, m):
    if sh["FNC"] == 0x50:
        #obj.printMessage(h, sh)
        mp = obj.parseStatusRegisters(sh["RestMessage"], sh["RegStart"], sh["RegLen"])
        print(mp)

#ser = serial.Serial('/dev/ttySC1', 38400, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
ser = serial.serial_for_url('socket://192.168.12.34:8899')
pcwu = ZPS(conHardId, conSoftId, devHardId, devSoftId, onMessage)
pcwu.readStatusRegisters(ser)
ser.close()
