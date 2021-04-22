from .base import BaseDevice

# Based on work by krzysztof1111111111
# https://www.elektroda.pl/rtvforum/topic3499254.html


class PCWU(BaseDevice):

    # PCWU is driven by PG-426-P01 (controller) and MG-426-P01 (executive module)
    # Below are the registers for the executive module, so no controller settings
    REG_MAX_ADR = 536
    REG_MAX_NUM = 226
    REG_CONFIG_START = 302

    # Interaction between status register 202 and config register 304:
    #
    # When talking to the executive module directly the heat pump can be (manually)
    # disabled and enabled through config register 304 and the result of this is visible
    # in status register 202. With the controller on this works as expected, the heat
    # pump can be put into a waiting mode where it will not turn on until enabled again
    # through register 304. With the controller off however this doesn't work. Maybe
    # the executive module is hardcoded to not turn the heat pump on when the controller
    # is off? See eavesDrop function in base device to learn how the executive module
    # knows that the controller is off. What makes this especially weird is that register
    # 202 changes its value to 0 when the controller is off even if register 304 says
    # otherwise. It would be great if we could detect the 'controller is off' situation
    # through one of the registers, but I haven't found a way yet.

    registers = {

        # Status registers
        120: { 'type': 'date', 'name': 'date' },                        # Date
        124: { 'type': 'time', 'name': 'time' },                        # Time
        128: { 'type': 'te10', 'name': 'T1' },                          # T1 (Ambient temp)
        130: { 'type': 'te10', 'name': 'T2' },                          # T2 (Tank bottom temp)
        132: { 'type': 'te10', 'name': 'T3' },                          # T3 (Tank top temp)
        138: { 'type': 'te10', 'name': 'T6' },                          # T6 (HP water inlet temp)
        140: { 'type': 'te10', 'name': 'T7' },                          # T7 (HP water outlet temp)
        142: { 'type': 'te10', 'name': 'T8' },                          # T8 (HP evaporator temp)
        144: { 'type': 'te10', 'name': 'T9' },                          # T9 (HP before compressor temp)
        146: { 'type': 'te10', 'name': 'T10' },                         # T10 (HP after compressor temp)

        194: { 'type': 'bool', 'name': 'IsManual' },
        196: { 'type': 'mask', 'name': [
            'FanON',                                                    # Fan ON (True/False)
            None,
            'CirculationPumpON',                                        # Circulation pump ON (True/False)
            None,
            None,
            'HeatPumpON',                                               # Heat pump ON (True/False)
            None,
            None,
            None,
            None,
            None,
            'CompressorON',                                             # Compressor ON (True/False)
            'HeaterEON',                                                # Heater E ON (True/False)
        ]},
        198: { 'type': 'word', 'name': 'EV1' },
        202: { 'type': 'word', 'name': 'WaitingStatus' },               # 0 when available for operation, 2 when disabled through register 304

        # Config registers
        302: { 'type': 'word', 'name': 'InstallationScheme' },          # Installation Scheme (1-9)
        304: { 'type': 'bool', 'name': 'HeatPumpEnabled' },             # Heat Pump Enabled (True/False)
        306: { 'type': 'word', 'name': 'TapWaterSensor' },              # Tap Water Sensor (0=T2, 1=T3, 2=T7)
        308: { 'type': 'te10', 'name': 'TapWaterTemp' },                # Tap Water Temp (Temperature at sensor above to turn heat pump off)
        310: { 'type': 'te10', 'name': 'TapWaterHysteresis' },          # Tap Water Hysteresis (Difference between sensor and value above to turn heat pump on)
        312: { 'type': 'te10', 'name': 'AmbientMinTemp' },              # Ambient Min Temp (Minimum T1 temperature to turn heat pump on)
        314: { 'type': 'tprg', 'name': 'TimeProgramHPM-F' },            # Time Program HP M-F (True/False per hour of the day)
        318: { 'type': 'tprg', 'name': 'TimeProgramHPSat' },            # Time Program HP Sat (True/False per hour of the day)
        322: { 'type': 'tprg', 'name': 'TimeProgramHPSun' },            # Time Program HP Sun (True/False per hour of the day)

        326: { 'type': 'bool', 'name': 'AntiFreezingEnabled' },         # Anti Freezing Enabled (True/False)
        328: { 'type': 'word', 'name': 'WaterPumpOperationMode' },      # Water Pump Operation Mode (0=Continuous, 1=Synchronous)
        330: { 'type': 'word', 'name': 'FanOperationMode' },            # Fan Operation Mode (0=Max, 1=Min, 2=Day/Night)
        332: { 'type': 'word', 'name': 'DefrostingInterval' },          # Defrosting Interval (min)
        334: { 'type': 'te10', 'name': 'DefrostingStartTemp' },         # Defrosting Start Temp
        336: { 'type': 'te10', 'name': 'DefrostingStopTemp' },          # Defrosting Stop Temp
        338: { 'type': 'word', 'name': 'DefrostingMaxTime' },           # Defrosting Max Time (min)

        #374                                                            # Time Program?
        #406                                                            # Time Program?
        #432                                                            # Time Program?
        #476                                                            # Time Program?

        516: { 'type': 'bool', 'name': 'ExtControllerHPOFF' },          # Ext Controller HP OFF (True/False)
        #518                                                            # Ext Controller E OFF?
        #520                                                            # Ext Controller P OFF?
        #522                                                            # Ext Controller .. OFF?
        #524                                                            # Ext Controller .. OFF?

    }

    def disable(self, ser):
        return self.writeRegister(ser, 304, 0)

    def enable(self, ser):
        return self.writeRegister(ser, 304, 1)
