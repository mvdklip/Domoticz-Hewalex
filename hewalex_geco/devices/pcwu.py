from .base import BaseDevice

# Based on work by krzysztof1111111111
# https://www.elektroda.pl/rtvforum/topic3499254.html


class PCWU(BaseDevice):

    # PCWU is driven by Geco PG-426-P01 (controller) and MG-426-P01 (executive module).
    # Below are the registers for the executive module; the controller follows closely.
    # Tested with firmware v0.1n and v0.1o (3,0kW), let me know if you use this with
    # v0.1m (2,5kW).
    REG_MAX_ADR = 536
    REG_MAX_NUM = 226
    REG_CONFIG_START = 302

    # Interaction between status registers 194 and 202 and config register 304:
    #
    # When talking to the executive module directly the heat pump can be (manually)
    # disabled and enabled through config register 304 and the result of this is visible
    # in status register 202. With the controller on this works as expected, the heat
    # pump can be put into a waiting mode where it will not turn on until enabled again
    # through register 304. With the controller off however this doesn't work. It looks
    # like the executive module is hardcoded to not turn the heat pump on as long as the
    # controller is off. See eavesDrop function in base device to learn how the executive
    # module knows that the controller is off. This situation can be read from register
    # 194 (IsManual), so for a full status multiple registers should be checked.
    #
    # For some reason writing a 1 to register 304 sometimes disabled instead of enabled
    # the heatpump. Writing a value of 255 prevented this for some reason. Please note
    # that this happened on v0.1n; since then I've exchanged controller and executive
    # module for v0.1o ones; now it doesn't seem to happen anymore.
    #
    # From the normal communication cycle between controller and executive module some
    # special registers can be identified. These are not available through this library,
    # but documented right here:
    #
    # 252: contains the status of the controller; examples:
    #   08000000 = display off
    #   10000000 = display on, no changes
    #   11000000 = display on, parameter changed;
    #       executive module responds by reading 8 controller registers starting at 256
    #   14000000 = display on, date/time changed;
    #       executive module responds by reading 8 controller registers starting at 120
    #
    # 256: contains the changed parameter in the controller; examples:
    #   00 01 0000 0000 => Enabled, Heatpump, False
    #   00 01 0100 0000 => Enabled, Heatpump, True
    #   02 01 c201 0000 => TapWaterTemp, Heatpump, 45.0
    #   02 02 a401 0000 => TapWaterTemp, Heater E, 42.0
    #   04 01 5A00 0000 => AmbientMinTemp, Heatpump, 9.0
    #

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

        166: { 'type': 'word', 'name': 'unknown5' },                    # Unknown, observed values are 1 (krzysztof1111111111) and 3 (mvdklip)
        192: { 'type': 'word', 'name': 'unknown3' },                    # Unknown, observed values are 49659, 49663 and 50175; probably a bitmask
        194: { 'type': 'word', 'name': 'IsManual' },                    # Unknown, 2 when controller on, 1 when controller off
        196: { 'type': 'mask', 'name': [                                # TODO - Add flags for Heater P, Boiler Pump, ...
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
        198: { 'type': 'word', 'name': 'EV1' },                         # Expansion Valve 1? - Otwarcie zaworu rozprężnego - Opening of the expansion valve
        202: { 'type': 'word', 'name': 'WaitingStatus' },               # 0 when available for operation, 2 when disabled through register 304, 4 when low COP, 32 when just stopped and waiting to be restarted
        206: { 'type': 'word', 'name': 'WaitingTimer' },                # Timer counting down to 0 when just stopped and waiting to be available for operation again
        210: { 'type': 'word', 'name': 'unknown7' },                    # Unknown, observed value is 0 and is possibly related to alarms
        218: { 'type': 'word', 'name': 'unknown8' },                    # Unknown, observed value is 0
        220: { 'type': 'word', 'name': 'unknown9' },                    # Unknown, observed value is 0
        222: { 'type': 'word', 'name': 'unknown10' },                   # Unknown, observed value is 0

        # Config registers - Heat Pump
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
        #340                                                            # Unknown, observed value is 20
        #342                                                            # Unknown, observed value is 5

        # Config registers - Expansion Valve
        344: { 'type': 'word', 'name': 'EVOperationMode' },             # Expansion Valve Operation Mode (0=Auto, 1=Manual)
        346: { 'type': 'word', 'name': 'EVManualStep' },                # Expansion Valve Manual Step (300)
        348: { 'type': 'te10', 'name': 'EVSuperheatTemp' },             # Expansion Valve Superheat Temp (1)
        350: { 'type': 'word', 'name': 'EVInitialStep' },               # Expansion Valve Initial Step (200)
        352: { 'type': 'word', 'name': 'EVMinStep' },                   # Expansion Valve Min Step (120)
        354: { 'type': 'word', 'name': 'EVDefrostingStep' },            # Expansion Valve Defrosting Step (480)

        # Config registers - Heater E
        364: { 'type': 'bool', 'name': 'HeaterEEnabled' },              # Heater E Enabled (True/False)
        366: { 'type': 'te10', 'name': 'HeaterEHPONTemp' },             # Heater E water temp when HP ON (45.0)
        368: { 'type': 'te10', 'name': 'HeaterEHPOFFTemp' },            # Heater E water temp when HP OFF (55.0)
        370: { 'type': 'bool', 'name': 'HeaterEBlocked' },              # Heater E blocked when HP on? (True/False)
        #372                                                            # Unknown, observed value is 1 / True
        374: { 'type': 'tprg', 'name': 'HeaterETimeProgramM-F' },       # Heater E Time Program M-F (True/False per hour of the day)
        378: { 'type': 'tprg', 'name': 'HeaterETimeProgramSat' },       # Heater E Time Program Sat (True/False per hour of the day)
        382: { 'type': 'tprg', 'name': 'HeaterETimeProgramSun' },       # Heater E Time Program Sun (True/False per hour of the day)

        # Config registers - Heater P
        396: { 'type': 'bool', 'name': 'HeaterPEnabled' },              # Heater P Enabled (True/False)
        398: { 'type': 'te10', 'name': 'HeaterPHPONTemp' },             # Heater P water temp when HP ON (45.0)
        400: { 'type': 'te10', 'name': 'HeaterPHPOFFTemp' },            # Heater P water temp when HP OFF (55.0)
        402: { 'type': 'bool', 'name': 'HeaterPBlocked' },              # Heater P blocked when HP on? (True/False)
        #404                                                            # Unknown, observed value is 1 / True
        406: { 'type': 'tprg', 'name': 'HeaterPTimeProgramM-F' },       # Heater P Time Program M-F (True/False per hour of the day)
        410: { 'type': 'tprg', 'name': 'HeaterPTimeProgramSat' },       # Heater P Time Program Sat (True/False per hour of the day)
        414: { 'type': 'tprg', 'name': 'HeaterPTimeProgramSun' },       # Heater P Time Program Sun (True/False per hour of the day)

        # Config registers - Circulation Pump C
        428: { 'type': 'te10', 'name': 'CirculationPumpMinTemp' },      # Circulation Pump Min Temp
        430: { 'type': 'word', 'name': 'CirculationPumpOperationMode' },# Circulation Pump Operation Mode (0=Continuous, 1=Interrupted)
        432: { 'type': 'tprg', 'name': 'CirculationPumpTimeProgramM-F' },# Circulation Pump Time Program M-F (True/False per hour of the day)
        436: { 'type': 'tprg', 'name': 'CirculationPumpTimeProgramSat' },# Circulation Pump Time Program Sat (True/False per hour of the day)
        440: { 'type': 'tprg', 'name': 'CirculationPumpTimeProgramSun' },# Circulation Pump Time Program Sun (True/False per hour of the day)

        # Config registers - Boiler Pump F - Solid Fuel Boiler B
        454: { 'type': 'te10', 'name': 'BoilerPumpMaxTemp' },           # Boiler Pump Max Temp (65.0)
        456: { 'type': 'te10', 'name': 'BoilerPumpMinTemp' },           # Boiler Pump Min Temp (45.0)
        458: { 'type': 'te10', 'name': 'BoilerPumpHysteresis' },        # Boiler Pump Hysteresis (8.0)
        460: { 'type': 'bool', 'name': 'BoilerPumpPriority' },          # Boiler Pump Priority (True/False)

        # Config registers - Unknown - Automatic Boiler D?
        #472                                                            # Unknown, observed value is 650 / 65.0
        #474                                                            # Unknown, observed value is 1 / True
        #476                                                            # Time Program?

        # Config registers - Anti-Legionella
        498: { 'type': 'bool', 'name': 'AntiLegionellaEnabled' },       # Anti-Legionella Enabled (True/False)
        500: { 'type': 'bool', 'name': 'AntiLegionellaUseHeaterE' },    # Anti-Legionella Use Heater E (True/False)
        502: { 'type': 'bool', 'name': 'AntiLegionellaUseHeaterP' },    # Anti-Legionella Use Heater P (True/False)
        #504                                                            # Unknown, observed value is 1 / True

        # Config registers - Ext Controller
        516: { 'type': 'bool', 'name': 'ExtControllerHPOFF' },          # Ext Controller HP OFF (True/False)
        518: { 'type': 'bool', 'name': 'ExtControllerHeaterEOFF' },     # Ext Controller Heater E OFF (True/False)
        #520                                                            # Unknown, observed value is 1 / True
        522: { 'type': 'bool', 'name': 'ExtControllerPumpFOFF' },       # Ext Controller Pump F OFF (True/False)
        524: { 'type': 'bool', 'name': 'ExtControllerHeaterPOFF' },     # Ext Controller Heater P OFF (True/False)

        # Config registers - Unknown
        #534                                                            # Unknown, observed value is 2
        #536                                                            # Unknown, observed value is 2
    }

    def disable(self, ser):
        return self.writeRegister(ser, 'HeatPumpEnabled', 0)

    def enable(self, ser):
        #return self.writeRegister(ser, 'HeatPumpEnabled', 255)          # Used to write a 1 to this register but this sometimes disabled (?!) the heatpump instead of enabling it
        return self.writeRegister(ser, 'HeatPumpEnabled', 1)

    def _setTemp(self, ser, regName, temp):
        return self.writeRegister(ser, regName, int(temp * 10))

    def setTapWaterTemp(self, ser, temp):
        return self._setTemp(ser, 'TapWaterTemp', temp)

    def setTapWaterHysteresis(self, ser, temp):
        return self._setTemp(ser, 'TapWaterHysteresis', temp)

    def setAmbientMinTemp(self, ser, temp):
        return self._setTemp(ser, 'AmbientMinTemp', temp)
