from binascii import hexlify, unhexlify

from .base import BaseDevice
from ..crc import *

# Based on work by aelias-eu
# https://github.com/aelias-eu/hewalex-geco-protocol


class ZPS(BaseDevice):
    registers = {
        120: { 'type': 'date', 'name': 'date' },                        # Date
        124: { 'type': 'time', 'name': 'time' },                        # Time
        128: { 'type': 'temp', 'name': 'T1' },                          # T1 (Collectors temp)
        130: { 'type': 'temp', 'name': 'T2' },                          # T2 (Tank bottom temp)
        132: { 'type': 'temp', 'name': 'T3' },                          # T3 (Air separator temp)
        134: { 'type': 'temp', 'name': 'T4' },                          # T4 (Tank top temp)
        136: { 'type': 'temp', 'name': 'T5' },                          # T5
        138: { 'type': 'temp', 'name': 'T6' },                          # T6
        144: { 'type': 'word', 'name': 'CollectorPower' },              # Collector Power (W)
        148: { 'type': 'fl10', 'name': 'Consumption' },                 # Consumption (W)
        150: { 'type': 'bool', 'name': 'CollectorActive' },             # Collector Active (True/False)
        152: { 'type': 'fl10', 'name': 'FlowRate' },                    # Flow Rate (l/min)
        154: { 'type': 'bool', 'name': 'CollectorPumpON' },             # Collector Pump ON (True/False)
        156: { 'type': 'word', 'name': 'CollectorPumpSpeed' },          # Collector Pump Speed (0-15)
        166: { 'type': 'fl10', 'name': 'TotalEnergy' },                 # Total Energy (kWh)
        170: { 'type': 'word', 'name': 'InstallationScheme' },          # Installation Scheme (1-19)
        172: { 'type': 'word', 'name': 'DisplayTimeout' },              # Display Timeout (1-10 min)
        174: { 'type': 'word', 'name': 'DisplayBrightness' },           # Display Brightness (1-10)
        176: { 'type': 'bool', 'name': 'AlarmSoundEnabled' },           # Alarm Sound Enabled (True/False)
        178: { 'type': 'bool', 'name': 'KeySoundEnabled' },             # Key Sound Enabled (True/False)
        180: { 'type': 'word', 'name': 'DisplayLanguage' },             # Display Language (0=PL, 1=EN, 2=DE, 3=FR, 4=PT, 5=ES, 6=NL, 7=IT, 8=CZ, 9=SL, ...)
        182: { 'type': 'temp', 'name': 'FluidFreezingTemp' },           # Fluid Freezing Temp
        186: { 'type': 'fl10', 'name': 'FlowRateNominal' },             # Flow Rate Nominal (l/min) (45)
        188: { 'type': 'word', 'name': 'FlowRateMeasurement' },         # Flow Rate Measurement (0=Rotameter, 1=Electronic G916, 2=Electronic)
        190: { 'type': 'f100', 'name': 'FlowRateWeight' },              # Flow Rate Weight (imp/l)
        192: { 'type': 'bool', 'name': 'HolidayEnabled' },              # Holiday Enabled (True/False)
        194: { 'type': 'word', 'name': 'HolidayStartDay' },             # Holiday Start Day
        196: { 'type': 'word', 'name': 'HolidayStartMonth' },           # Holiday Start Month
        198: { 'type': 'word', 'name': 'HolidayStartYear' },            # Holiday Start Year
        200: { 'type': 'word', 'name': 'HolidayEndDay' },               # Holiday End Day
        202: { 'type': 'word', 'name': 'HolidayEndMonth' },             # Holiday End Month
        204: { 'type': 'word', 'name': 'HolidayEndYear' },              # Holiday End Year
        206: { 'type': 'word', 'name': 'CollectorType' },               # Collector Type (0=Flat, 1=Tube)
        208: { 'type': 'temp', 'name': 'CollectorPumpHysteresis' },     # Collector Pump Hysteresis (Difference between T1 and T2 to turn on collector pump)
        210: { 'type': 'temp', 'name': 'ExtraPumpHysteresis' },         # Extra Pump Hysteresis (Temp difference to turn on extra pump)
        212: { 'type': 'temp', 'name': 'CollectorPumpMaxTemp' },        # Collector Pump Max Temp (Maximum T2 temp to turn off collector pump)
        214: { 'type': 'word', 'name': 'BoilerPumpMinTemp' },           # Boiler Pump Min Temp (Minimum T5 temp to turn on boiler pump)
        218: { 'type': 'word', 'name': 'HeatSourceMaxTemp' },           # Heat Source Max Temp (Maximum T4 temp to turn off heat sources)
        220: { 'type': 'word', 'name': 'BoilerPumpMaxTemp' },           # Boiler Pump Max Temp (Maximum T4 temp to turn off boiler pump)
        222: { 'type': 'bool', 'name': 'PumpRegulationEnabled' },       # Pump Regulation Enabled (True/False)
        226: { 'type': 'word', 'name': 'HeatSourceMaxCollectorPower' }, # Heat Source Max Collector Power (Maximum collector power to turn off heat sources) (100-9900W)
        228: { 'type': 'bool', 'name': 'CollectorOverheatProtEnabled' },# Collector Overheat Protection Enabled (True/False)
        230: { 'type': 'temp', 'name': 'CollectorOverheatProtMaxTemp' },# Collector Overheat Protection Max Temp (Maximum T2 temp for overheat protection)
        232: { 'type': 'bool', 'name': 'CollectorFreezingProtEnabled' },# Collector Freezing Protection Enabled (True/False)
        234: { 'type': 'word', 'name': 'HeatingPriority' },             # Heating Priority
        236: { 'type': 'bool', 'name': 'LegionellaProtEnabled' },       # Legionella Protection Enabled (True/False)
        238: { 'type': 'bool', 'name': 'LockBoilerKWithBoilerC' },      # Lock Boiler K With Boiler C (True/False)
        240: { 'type': 'bool', 'name': 'NightCoolingEnabled' },         # Night Cooling Enabled (True/False)
        242: { 'type': 'temp', 'name': 'NightCoolingStartTemp' },       # Night Cooling Start Temp
        244: { 'type': 'temp', 'name': 'NightCoolingStopTemp' },        # Night Cooling Stop Temp
        246: { 'type': 'word', 'name': 'NightCoolingStopTime' },        # Night Cooling Stop Time (hr)
        248: { 'type': 'word', 'name': 'TimeProgramCMoFr1' },           # Time Program C Mo-Fr #1 (0xFFC0)
        250: { 'type': 'word', 'name': 'TimeProgramCMoFr2' },           # Time Program C Mo-Fr #2 (0x3F)
        252: { 'type': 'word', 'name': 'TimeProgramCSa1' },             # Time Program C Sa #1 (0xFF80)
        254: { 'type': 'word', 'name': 'TimeProgramCSa2' },             # Time Program C Sa #2 (0x3F)
        256: { 'type': 'word', 'name': 'TimeProgramCSu1' },             # Time Program C Su #1 (0xFF80)
        258: { 'type': 'word', 'name': 'TimeProgramCSu2' },             # Time Program C Su #2 (0x3F)
        260: { 'type': 'word', 'name': 'TimeProgramKMoFr1' },           # Time Program K Mo-Fr #1 (0xFFC0)
        262: { 'type': 'word', 'name': 'TimeProgramKMoFr2' },           # Time Program K Mo-Fr #2 (0x3F)
        264: { 'type': 'word', 'name': 'TimeProgramKSa1' },             # Time Program K Sa #1 (0xFF80)
        266: { 'type': 'word', 'name': 'TimeProgramKSa2' },             # Time Program K Sa #2 (0x3F)
        268: { 'type': 'word', 'name': 'TimeProgramKSu1' },             # Time Program K Su #1 (0xFF80)
        270: { 'type': 'word', 'name': 'TimeProgramKSu2' },             # Time Program K Su #2 (0x3F)
        278: { 'type': 'word', 'name': 'CollectorPumpMinRev' },         # Collector Pump Min Rev (rev/min)
        280: { 'type': 'word', 'name': 'CollectorPumpMaxRev' },         # Collector Pump Max Rev (rev/min)
        282: { 'type': 'word', 'name': 'CollectorPumpMinIncTime' },     # Collector Pump Min Increase Time (s)
        284: { 'type': 'word', 'name': 'CollectorPumpMinDecTime' },     # Collector Pump Min Decrease Time (s)
        286: { 'type': 'word', 'name': 'CollectorPumpStartupSpeed' },   # Collector Pump Startup Speed (1-15)
        288: { 'type': 'bool', 'name': 'PressureSwitchEnabled' },       # Pressure Switch Enabled (True/False)
        290: { 'type': 'bool', 'name': 'TankOverheatProtEnabled' },     # Tank Overheat Protection Enabled (True/False)
        320: { 'type': 'word', 'name': 'Reg320' },                      # This one is interesting; it changes constantly
        322: { 'type': 'bool', 'name': 'CirculationPumpEnabled' },      # Circulation Pump Enabled (True/False)
        324: { 'type': 'word', 'name': 'CirculationPumpMode' },         # Circulation Pump Mode (0=Discontinuous, 1=Continuous)
        326: { 'type': 'temp', 'name': 'CirculationPumpMinTemp' },      # Circulation Pump Min Temp (Minimum T4 temp to turn on circulation pump)
        328: { 'type': 'word', 'name': 'CirculationPumpONTime' },       # Circulation Pump ON Time (1-59min)
        330: { 'type': 'word', 'name': 'CirculationPumpOFFTime' },      # Circulation Pump OFF Time (1-59min)
    }

    def readStatusRegisters(self, ser):
        # we can read registers between 100 and 330
        # we can read max 76 registers at a time
        # the most interesting registers start at 120
        return self.readRegisters(ser, 120, 76)
        #return self.readRegisters(ser, 196, 76)
        #return self.readRegisters(ser, 272, 60)
