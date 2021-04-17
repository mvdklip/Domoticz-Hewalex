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

        302: { 'type': 'word', 'name': 'InstallationScheme' },          # Installation Scheme (1-9)
        304: { 'type': 'bool', 'name': 'HeatPumpEnabled' },             # Heat Pump Enabled (True/False)
        306: { 'type': 'word', 'name': 'TapWaterSensor' },              # Tap Water Sensor (0=T2, 1=T3, 2=T7)
        308: { 'type': 'te10', 'name': 'TapWaterTemp' },                # Tap Water Temp (Temperature at sensor above to turn heat pump off)
        310: { 'type': 'te10', 'name': 'TapWaterHysteresis' },          # Tap Water Hysteresis (Difference between sensor and value above to turn heat pump on)
        312: { 'type': 'te10', 'name': 'AmbientMinTemp' },              # Ambient Min Temp (Minimum T1 temperature to turn heat pump on)

        326: { 'type': 'bool', 'name': 'AntiFreezingEnabled' },         # Anti Freezing Enabled (True/False)
        328: { 'type': 'word', 'name': 'WaterPumpOperationMode' },      # Water Pump Operation Mode (0=Continuous, 1=Synchronous)
        330: { 'type': 'word', 'name': 'FanOperationMode' },            # Fan Operation Mode (0=Max, 1=Min, 2=Day/Night)
        332: { 'type': 'word', 'name': 'DefrostingInterval' },          # Defrosting Interval (min)
        334: { 'type': 'te10', 'name': 'DefrostingStartTemp' },         # Defrosting Start Temp
        336: { 'type': 'te10', 'name': 'DefrostingStopTemp' },          # Defrosting Stop Temp
        338: { 'type': 'word', 'name': 'DefrostingMaxTime' },           # Defrosting Max Time (min)
    }

    def readStatusRegisters(self, ser):
        # we can read registers between 100 and 536
        # we can read max 226 registers at a time
        # registers below 256 (dubbed 'status registers') are read-only
        # the most interesting registers start at 120
        # in eavesdropping mode some pumps send 92 registers, others send 104; why is unknown
        return self.readRegisters(ser, 120, 92)

    def disable(self, ser):
        return self.writeRegister(ser, 304, 0)

    def enable(self, ser):
        return self.writeRegister(ser, 304, 1)
