from .base import BaseDevice

# Based on work by aelias-eu
# https://github.com/aelias-eu/hewalex-geco-protocol


class ZPS(BaseDevice):

    # ZPS is driven by G-422-P09 (controller)
    # Below are the registers for the controller, so including controller settings
    REG_MAX_ADR = 330
    REG_MAX_NUM = 76
    REG_CONFIG_START = 170

    registers = {

        # Status registers
        120: { 'type': 'date', 'name': 'date',                          'desc': 'Date' },
        124: { 'type': 'time', 'name': 'time',                          'desc': 'Time' },
        128: { 'type': 'temp', 'name': 'T1',                            'desc': 'T1 (Collectors temp)' },
        130: { 'type': 'temp', 'name': 'T2',                            'desc': 'T2 (Tank bottom temp)' },
        132: { 'type': 'temp', 'name': 'T3',                            'desc': 'T3 (Air separator temp)' },
        134: { 'type': 'temp', 'name': 'T4',                            'desc': 'T4 (Tank top temp)' },
        136: { 'type': 'temp', 'name': 'T5',                            'desc': 'T5 (Boiler outlet temp)' },
        138: { 'type': 'temp', 'name': 'T6',                            'desc': 'T6 (Void)' },
        144: { 'type': 'word', 'name': 'CollectorPower',                'desc': 'Collector Power (W)' },
        148: { 'type': 'fl10', 'name': 'Consumption',                   'desc': 'Consumption (W)' },
        150: { 'type': 'bool', 'name': 'CollectorActive',               'desc': 'Collector Active (True/False)' },
        152: { 'type': 'fl10', 'name': 'FlowRate',                      'desc': 'Flow Rate (l/min)' },
        154: { 'type': 'mask', 'name': [
            'CollectorPumpON',                                          # Collector Pump (P) ON (True/False)
            None,                                                       # Boiler Pump (K) ON?
            'CirculationPumpON',                                        # Circulation Pump (C) ON (True/False)
        ]},
        156: { 'type': 'word', 'name': 'CollectorPumpSpeed',            'desc': 'Collector Pump Speed (0-15)' },
        166: { 'type': 'fl10', 'name': 'TotalEnergy',                   'desc': 'Total Energy (kWh)' },

        # Config registers
        170: { 'type': 'word', 'name': 'InstallationScheme',            'desc': 'Installation Scheme (1-19)' },
        172: { 'type': 'word', 'name': 'DisplayTimeout',                'desc': 'Display Timeout (1-10 min)' },
        174: { 'type': 'word', 'name': 'DisplayBrightness',             'desc': 'Display Brightness (1-10)' },
        176: { 'type': 'bool', 'name': 'AlarmSoundEnabled',             'desc': 'Alarm Sound Enabled (True/False)' },
        178: { 'type': 'bool', 'name': 'KeySoundEnabled',               'desc': 'Key Sound Enabled (True/False)' },
        180: { 'type': 'word', 'name': 'DisplayLanguage',               'desc': 'Display Language (0=PL, 1=EN, 2=DE, 3=FR, 4=PT, 5=ES, 6=NL, 7=IT, 8=CZ, 9=SL, ...)' },
        182: { 'type': 'temp', 'name': 'FluidFreezingTemp',             'desc': 'Fluid Freezing Temp' },
        186: { 'type': 'fl10', 'name': 'FlowRateNominal',               'desc': 'Flow Rate Nominal (l/min)' },
        188: { 'type': 'word', 'name': 'FlowRateMeasurement',           'desc': 'Flow Rate Measurement (0=Rotameter, 1=Electronic G916, 2=Electronic)' },
        190: { 'type': 'f100', 'name': 'FlowRateWeight',                'desc': 'Flow Rate Weight (imp/l)' },
        192: { 'type': 'bool', 'name': 'HolidayEnabled',                'desc': 'Holiday Enabled (True/False)' },
        194: { 'type': 'word', 'name': 'HolidayStartDay',               'desc': 'Holiday Start Day' },
        196: { 'type': 'word', 'name': 'HolidayStartMonth',             'desc': 'Holiday Start Month' },
        198: { 'type': 'word', 'name': 'HolidayStartYear',              'desc': 'Holiday Start Year' },
        200: { 'type': 'word', 'name': 'HolidayEndDay',                 'desc': 'Holiday End Day' },
        202: { 'type': 'word', 'name': 'HolidayEndMonth',               'desc': 'Holiday End Month' },
        204: { 'type': 'word', 'name': 'HolidayEndYear',                'desc': 'Holiday End Year' },
        206: { 'type': 'word', 'name': 'CollectorType',                 'desc': 'Collector Type (0=Flat, 1=Tube)' },
        208: { 'type': 'temp', 'name': 'CollectorPumpHysteresis',       'desc': 'Collector Pump Hysteresis (Difference between T1 and T2 to turn on collector pump)' },
        210: { 'type': 'temp', 'name': 'ExtraPumpHysteresis',           'desc': 'Extra Pump Hysteresis (Temp difference to turn on extra pump)' },
        212: { 'type': 'temp', 'name': 'CollectorPumpMaxTemp',          'desc': 'Collector Pump Max Temp (Maximum T2 temp to turn off collector pump)' },
        214: { 'type': 'word', 'name': 'BoilerPumpMinTemp',             'desc': 'Boiler Pump Min Temp (Minimum T5 temp to turn on boiler pump)' },
        218: { 'type': 'word', 'name': 'HeatSourceMaxTemp',             'desc': 'Heat Source Max Temp (Maximum T4 temp to turn off heat sources)' },
        220: { 'type': 'word', 'name': 'BoilerPumpMaxTemp',             'desc': 'Boiler Pump Max Temp (Maximum T4 temp to turn off boiler pump)' },
        222: { 'type': 'bool', 'name': 'PumpRegulationEnabled',         'desc': 'Pump Regulation Enabled (True/False)' },
        226: { 'type': 'word', 'name': 'HeatSourceMaxCollectorPower',   'desc': 'Heat Source Max Collector Power (Maximum collector power to turn off heat sources) (100-9900W)' },
        228: { 'type': 'bool', 'name': 'CollectorOverheatProtEnabled',  'desc': 'Collector Overheat Protection Enabled (True/False)' },
        230: { 'type': 'temp', 'name': 'CollectorOverheatProtMaxTemp',  'desc': 'Collector Overheat Protection Max Temp (Maximum T2 temp for overheat protection)' },
        232: { 'type': 'bool', 'name': 'CollectorFreezingProtEnabled',  'desc': 'Collector Freezing Protection Enabled (True/False)' },
        234: { 'type': 'word', 'name': 'HeatingPriority',               'desc': 'Heating Priority' },
        236: { 'type': 'bool', 'name': 'LegionellaProtEnabled',         'desc': 'Legionella Protection Enabled (True/False)' },
        238: { 'type': 'bool', 'name': 'LockBoilerKWithBoilerC',        'desc': 'Lock Boiler K With Boiler C (True/False)' },
        240: { 'type': 'bool', 'name': 'NightCoolingEnabled',           'desc': 'Night Cooling Enabled (True/False)' },
        242: { 'type': 'temp', 'name': 'NightCoolingStartTemp',         'desc': 'Night Cooling Start Temp (45-80)' },
        244: { 'type': 'temp', 'name': 'NightCoolingStopTemp',          'desc': 'Night Cooling Stop Temp (20-40)' },
        246: { 'type': 'word', 'name': 'NightCoolingStopTime',          'desc': 'Night Cooling Stop Time (hr)' },
        248: { 'type': 'tprg', 'name': 'TimeProgramCM-F',               'desc': 'Time Program C M-F (True/False per hour of the day)' },
        252: { 'type': 'tprg', 'name': 'TimeProgramCSat',               'desc': 'Time Program C Sat (True/False per hour of the day)' },
        256: { 'type': 'tprg', 'name': 'TimeProgramCSun',               'desc': 'Time Program C Sun (True/False per hour of the day)' },
        260: { 'type': 'tprg', 'name': 'TimeProgramKM-F',               'desc': 'Time Program K M-F (True/False per hour of the day)' },
        264: { 'type': 'tprg', 'name': 'TimeProgramKSat',               'desc': 'Time Program K Sat (True/False per hour of the day)' },
        268: { 'type': 'tprg', 'name': 'TimeProgramKSun',               'desc': 'Time Program K Sun (True/False per hour of the day)' },
        278: { 'type': 'word', 'name': 'CollectorPumpMinRev',           'desc': 'Collector Pump Min Rev (rev/min)' },
        280: { 'type': 'word', 'name': 'CollectorPumpMaxRev',           'desc': 'Collector Pump Max Rev (rev/min)' },
        282: { 'type': 'word', 'name': 'CollectorPumpMinIncTime',       'desc': 'Collector Pump Min Increase Time (s)' },
        284: { 'type': 'word', 'name': 'CollectorPumpMinDecTime',       'desc': 'Collector Pump Min Decrease Time (s)' },
        286: { 'type': 'word', 'name': 'CollectorPumpStartupSpeed',     'desc': 'Collector Pump Startup Speed (1-15)' },
        288: { 'type': 'bool', 'name': 'PressureSwitchEnabled',         'desc': 'Pressure Switch Enabled (True/False)' },
        290: { 'type': 'bool', 'name': 'TankOverheatProtEnabled',       'desc': 'Tank Overheat Protection Enabled (True/False)' },
        322: { 'type': 'bool', 'name': 'CirculationPumpEnabled',        'desc': 'Circulation Pump Enabled (True/False)' },
        324: { 'type': 'word', 'name': 'CirculationPumpMode',           'desc': 'Circulation Pump Mode (0=Discontinuous, 1=Continuous)' },
        326: { 'type': 'temp', 'name': 'CirculationPumpMinTemp',        'desc': 'Circulation Pump Min Temp (Minimum T4 temp to turn on circulation pump)' },
        328: { 'type': 'word', 'name': 'CirculationPumpONTime',         'desc': 'Circulation Pump ON Time (1-59 min)' },
        330: { 'type': 'word', 'name': 'CirculationPumpOFFTime',        'desc': 'Circulation Pump OFF Time (1-59 min)' },

        # Weird registers
        312: { 'type': 'dwrd', 'name': 'TotalOperationTime',            'desc': 'Total Operation Time (min) - lives in config space but is status register' },
        320: { 'type': 'word', 'name': 'Reg320',                        'desc': 'Unknown register - value changes constantly' },
    }

    def disableNightCooling(self, ser):
        return self.writeRegister(ser, 'NightCoolingEnabled', 0)

    def enableNightCooling(self, ser):
        return self.writeRegister(ser, 'NightCoolingEnabled', 1)

    def setNightCoolingStartTemp(self, ser, temp):
        return self._setTemp(ser, 'NightCoolingStartTemp', temp, 1)

    def setNightCoolingStopTemp(self, ser, temp):
        return self._setTemp(ser, 'NightCoolingStopTemp', temp, 1)
