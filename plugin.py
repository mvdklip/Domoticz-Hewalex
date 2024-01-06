# Hewalex Python Plugin for Domoticz
#
# Authors: mvdklip
#
# Based on
#
# https://www.elektroda.pl/rtvforum/topic3499254.html
# https://github.com/aelias-eu/hewalex-geco-protocol
#
# Serial port encoding config

# Parity

# 0: serial.PARITY_NONE
# 1: serial.PARITY_EVEN
# 2: serial.PARITY_ODD
# 3: serial.PARITY_MARK
# 4: serial.PARITY_SPACE

# Stop bits

# 0: serial.STOPBITS_ONE
# 8: serial.STOPBITS_ONE_POINT_FIVE
# 16: serial.STOPBITS_TWO
# Note that 1.5 stop bits are not supported on POSIX. It will fall back to 2 stop bits.

# Byte size

# 0: serial.FIVEBITS
# 32: serial.SIXBITS
# 64: serial.SEVENBITS
# 96: serial.EIGHTBITS

# Baud
# 3000: 300
# 6000: 600
# 12000: 1200
# 18000: 1800
# 24000: 2400
# 48000: 4800
# 96000: 9600
# 192000: 19200
# 384000: 38400
# 570000: 57600
# 1152000: 115200
"""
<plugin key="Hewalex" name="Hewalex" author="mvdklip" version="0.8.0">
    <description>
        <h2>Hewalex Plugin</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Register boiler temperatures and more</li>
        </ul>
    </description>
    <params>
        <param field="SerialPort" label="Serial port" width="200px" default="/dev/ttyUSB0"/>
        <param field="Address" label="IP Address" width="200px" />
        <param field="Port" label="Port" width="30px" default="8899"/>
        <param field="Mode1" label="IP or Serial" width="200px" required="true">
            <options>
                <option label="Use IP address" value="0" default="true"/>
                <option label="Serial - 9600-8-N-1" value="96096"/>
                <option label="Serial - 19200-8-N-1" value="192096"/>
                <option label="Serial - 28800-8-N-1" value="288096"/>
                <option label="Serial - 38400-8-N-1" value="384096"/>
                <option label="Serial - 57600-8-N-1" value="576096"/>
                <option label="Serial - 76800-8-N-1" value="768096"/>
                <option label="Serial - 115200-8-N-1" value="1152096"/>
            </options>
        </param>
        <param field="Mode2" label="Device & Mode" width="200px" required="true">
            <options>
                <option label="PCWU - Eavesdropping" value="1" default="true"/>
                <option label="PCWU - Direct comms" value="2"/>
                <option label="ZPS - Direct comms" value="3"/>
            </options>
        </param>
        <param field="Mode3" label="Query interval" width="75px" required="true">
            <options>
                <option label="15 sec" value="3"/>
                <option label="30 sec" value="6"/>
                <option label="1 min" value="12" default="true"/>
                <option label="3 min" value="36"/>
                <option label="5 min" value="60"/>
                <option label="10 min" value="120"/>
                <option label="30 min" value="360"/>
                <option label="60 min" value="720"/>
            </options>
        </param>
        <param field="Mode4" label="Controller and device Ids" width="75px" required="true" default="1,1;2,2"/>
        <param field="Mode5" label="Expert mode" width="75px">
            <options>
                <option label="True" value="Enabled"/>
                <option label="False" value="Disabled" default="true"/>
            </options>
        </param>
        <param field="Mode6" label="Debug log" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""


import serial
import time
import Domoticz

from hewalex_geco.devices import PCWU, ZPS


class BasePlugin:
    enabled = False
    lastPolled = 0
    baseUrl = None
    maxAttempts = 3

    conHardId = 1
    conSoftId = 1       # Controller hard and soft Ids
    devHardId = 2
    devSoftId = 2       # Device hard and soft Ids

    serialConfig = 0    # Default IP mode, so 0, none 0 --> serial parameters
    serialPort = None   # Device to access serial port on, such as /Dev/ttyUSB0
    devMode = None      # Operating mode of device (1 = PCWU - Eavesdropping, 2 = PCWU - Direct comms, 3 = ZPS - Direct comms)
    devReady = False    # Is device ready to accept commands?

    expertMode = False  # Expert mode enabled?

    serial_parameters = {}
    temp_devices = {}
    switch_devices = {}
    custom_devices = {}
    x_switch_devices = {}
    x_custom_devices = {}

    custom_data = {}

    def __init__(self):
        return

    def onStart(self):
        Domoticz.Debug("onStart called")

        self.serialConfig = int(Parameters["Mode1"])

        self.devMode = int(Parameters["Mode2"])
        Domoticz.Debug("Device & Mode is set to %d" % self.devMode)

        self.expertMode = (self.devMode > 1 and Parameters["Mode5"] == "Enabled")
        if self.expertMode:
            Domoticz.Debug("Expert mode and devices enabled")

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        else:
            Domoticz.Debugging(0)

        if self.serialConfig == 0
            self.baseUrl = "socket://%s:%s" % (Parameters["Address"], Parameters["Port"])
            Domoticz.Debug("Base URL is set to %s" % self.baseUrl)
        else
            self.serialPort = Parameters["SerialPort"]
            self.serial_parameters = decode_serial_parameters(self.serialConfig)
            Domoticz.Debug("Serial config is set to %s" % self.serial_parameters)
            
            
        allIds = Parameters["Mode4"].split(";")
        if len(allIds) == 2:
            conIds = allIds[0].split(',')
            if len(conIds) == 2:
                self.conHardId = int(conIds[0])
                self.conSoftId = int(conIds[1])
                Domoticz.Debug("Controller Ids set to %d, %d" % (self.conHardId, self.conSoftId))
            devIds = allIds[1].split(',')
            if len(devIds) == 2:
                self.devHardId = int(devIds[0])
                self.devSoftId = int(devIds[1])
                Domoticz.Debug("Device Ids set to %d, %d" % (self.devHardId, self.devSoftId))

        # PCWU devices
        if self.devMode == 1 or self.devMode == 2:
            SetupDevicesPCWU(self)
            if self.expertMode:
                SetupExpertDevicesPCWU(self)

        # ZPS devices
        elif (self.devMode == 3):
            SetupDevicesZPS(self)
            if self.expertMode:
                SetupExpertDevicesZPS(self)

        DumpConfigToLog()

        Domoticz.Heartbeat(5)

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onMessagePCWU(self, dev, h, sh, m):
        Domoticz.Debug("onMessagePCWU called")
        if (self.devMode == 1 and sh["FNC"] == 0x60) or (self.devMode == 2 and sh["FNC"] == 0x50):
            mp = dev.parseRegisters(sh["RestMessage"], sh["RegStart"], sh["RegLen"])

            # Device status
            if 'WaitingStatus' in mp:
                devReady, devStatus, devWaiting, devProgram, devError = PCWUStatus(mp)
                self.devReady = devReady if self.devMode == 2 else False

            # Temp and switch devices
            for k,v in self.temp_devices.items():
                if k in mp:
                    Devices[v].Update(nValue=0, sValue=str(mp[k]))
            for k,v in self.switch_devices.items():
                if k in mp:
                    newValue = int(mp[k])
                    if newValue != Devices[v].nValue:
                        Devices[v].Update(nValue=newValue, sValue="")

            # Custom devices
            for k,v in self.custom_devices.items():
                if k == 'CompressorON - Count' and 'CompressorON' in mp and 'CompressorON' in self.custom_data:
                    newValue = 1 if mp['CompressorON'] and not self.custom_data['CompressorON'] else 0
                    Devices[v].Update(nValue=0, sValue=str(newValue))
                elif k == 'CompressorON - Time' and 'CompressorON' in mp and 'CompressorONTime' in self.custom_data:
                    newValue = round(time.time() - self.custom_data['CompressorONTime']) if mp['CompressorON'] else 0
                    Devices[v].Update(nValue=0, sValue=str(newValue))
                elif k == 'Delta T' and 'T6' in mp and 'T7' in mp and 'CompressorON' in self.custom_data:
                    newValue = (mp['T7'] - mp['T6']) if self.custom_data['CompressorON'] else 0
                    Devices[v].Update(nValue=0, sValue=str(newValue))
                elif k in mp:
                    Devices[v].Update(nValue=0, sValue=str(mp[k]))

            if 'CompressorON' in mp:
                self.custom_data['CompressorON'] = mp['CompressorON']
                self.custom_data['CompressorONTime'] = time.time()

            # Expert devices
            if self.expertMode:
                for k,v in self.x_switch_devices.items():
                    if k in mp:
                        newValue = int(mp[k])
                        if newValue != Devices[v].nValue:
                            Devices[v].Update(nValue=newValue, sValue="")
                for k,v in self.x_custom_devices.items():
                    if k in mp:
                        if k == 'InstallationScheme':
                            newValue = min(max(int(mp[k]), 1), 9) * 10
                        elif k == 'WaterPumpOperationMode':
                            newValue = min(max(int(mp[k]), 0), 1) * 10
                        else:
                            newValue = min(max(int(mp[k]), 0), 2) * 10
                        Devices[v].Update(nValue=0, sValue=str(newValue))

    def onMessageZPS(self, dev, h, sh, m):
        Domoticz.Debug("onMessageZPS called")
        if (sh["FNC"] == 0x50):
            mp = dev.parseRegisters(sh["RestMessage"], sh["RegStart"], sh["RegLen"])

            # Device status
            if self.devMode == 3:
                self.devReady = True

            # Temp and switch devices
            for k,v in self.temp_devices.items():
                if k in mp:
                    Devices[v].Update(nValue=0, sValue=str(mp[k]))
            for k,v in self.switch_devices.items():
                if k in mp:
                    newValue = int(mp[k])
                    if newValue != Devices[v].nValue:
                        Devices[v].Update(nValue=newValue, sValue="")

            # Custom devices
            for k,v in self.custom_devices.items():
                if k == 'SWH kWh Total' and 'TotalEnergy' in mp:
                    Devices[v].Update(nValue=0, sValue=str(mp['TotalEnergy']))
                elif k == 'SWH Generation' and 'TotalEnergy' in mp and 'CollectorPower' in mp:
                    Devices[v].Update(nValue=0, sValue=str(mp['CollectorPower'])+";"+str(mp['TotalEnergy'] * 1000))
                elif k == 'SWH Consumption' and 'Consumption' in mp:
                    Devices[v].Update(nValue=0, sValue=str(mp['Consumption'])+";0")

            # Expert devices
            if self.expertMode:
                for k,v in self.x_switch_devices.items():
                    if k in mp:
                        newValue = int(mp[k])
                        if newValue != Devices[v].nValue:
                            Devices[v].Update(nValue=newValue, sValue="")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for unit %d with command %s, level %s." % (Unit, Command, Level))

        if self.devReady:

            # PCWU specific command handling
            if (self.devMode == 2):
                if (Unit == 5) and (Command == "Set Level"):
                    SendCommand(self, 'setTapWaterTemp', Level)
                    Devices[Unit].Update(nValue=0, sValue=str(Level))

            # ZPS specific command handling
            elif (self.devMode == 3):
                if (Unit == 9) and (Command == "Set Level"):
                    SendCommand(self, 'setTemp', 'NightCoolingStartTemp', Level)
                    Devices[Unit].Update(nValue=0, sValue=str(Level))
                elif (Unit == 10) and (Command == "Set Level"):
                    SendCommand(self, 'setTemp', 'NightCoolingStopTemp', Level)
                    Devices[Unit].Update(nValue=0, sValue=str(Level))
                elif (Unit == 11) and (Command == "Set Level"):
                    SendCommand(self, 'setTemp', 'CollectorPumpMaxTemp', Level)
                    Devices[Unit].Update(nValue=0, sValue=str(Level))
                elif (Unit == 12) and (Command == "Set Level"):
                    SendCommand(self, 'setTemp', 'CollectorOverheatProtMaxTemp', Level)
                    Devices[Unit].Update(nValue=0, sValue=str(Level))

            # Generic switch command handling
            if (self.devMode > 1):
                for k,v in self.switch_devices.items():
                    if (Unit == v):
                        nValue = 1 if (Command == "On") else 0
                        SendCommand(self, 'writeRegister', k, nValue)
                        Devices[Unit].Update(nValue=nValue, sValue="")
                if self.expertMode:
                    for k,v in self.x_switch_devices.items():
                        if (Unit == v):
                            nValue = 1 if (Command == "On") else 0
                            SendCommand(self, 'writeRegister', k, nValue)
                            Devices[Unit].Update(nValue=nValue, sValue="")
                    for k,v in self.x_custom_devices.items():
                        if (Unit == v):
                            if k == 'InstallationScheme':
                                nValue = min(max(int(Level / 10), 1), 9)
                            elif k == 'WaterPumpOperationMode':
                                nValue = min(max(int(Level / 10), 0), 1)
                            else:
                                nValue = min(max(int(Level / 10), 0), 2)
                            SendCommand(self, 'writeRegister', k, nValue)
                            Devices[Unit].Update(nValue=0, sValue=str(Level))

            return True     # TODO - check if command actually succeeded

        else:
            Domoticz.Debug("Device is not ready, ignoring command...")
            return False

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called %d" % self.lastPolled)

        if self.lastPolled == 0:
            attempt = 1

            while True:
                if attempt <= self.maxAttempts:
                    if attempt > 1:
                        Domoticz.Debug("Previous attempt failed, trying again...")
                else:
                    Domoticz.Error("Failed to retrieve data from %s, cancelling..." % self.baseUrl)
                    break
                attempt += 1

                try:
                    if (self.devMode == 1):
                        SendCommand(self, 'eavesDrop')
                    else:
                        SendCommand(self, 'readStatusRegisters')
                        SendCommand(self, 'readConfigRegisters')
                except Exception as e:
                    Domoticz.Log("Exception from %s; %s" % (self.baseUrl, e))
                    self.devReady = False
                else:
                    break

        self.lastPolled += 1
        self.lastPolled %= int(Parameters["Mode3"])


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


# Generic helper functions
PCWU_STATUS_OFF = 0         # Turned OFF through controller
PCWU_STATUS_WAITING = 10    # Waiting for some condition to clear (see below)
PCWU_STATUS_IDLE = 20       # Idle
PCWU_STATUS_RUNNING = 30    # Running program (see below)
PCWU_STATUS_ERROR = 40      # Error condition (see below)

PCWU_WAITING_NONE = 0       # Not waiting
PCWU_WAITING_EXTOFF = 10    # Ext OFF contact closed
PCWU_WAITING_HPOFF = 20     # Disabled through controller menu (reg 304)
PCWU_WAITING_STOP = 30      # Temporarily disabled while counting down
PCWU_WAITING_LOWCOP = 40    # Ambient temperature too low

PCWU_PROGRAM_NONE = 0       # No program running
PCWU_PROGRAM_HEAT = 10      # Tap water heating program
PCWU_PROGRAM_DEFROST = 20   # Evaporator defrost program
PCWU_PROGRAM_LOWTEMP = 30   # Tank antifreeze protection
PCWU_PROGRAM_ANTIFREEZ = 40 # HP antifreeze protection
PCWU_PROGRAM_PREHEAT = 50   # Compressor preheat program

PCWU_ERROR_NONE = 0
PCWU_ERROR_LOWPRES = 10     # Low pressure (alarm 17)
PCWU_ERROR_HIGHPRES = 20    # High pressure (alarm 18)
PCWU_ERROR_OVERTEMP = 30    # Over temp (alarm 21)

def PCWUStatus(mp):
    devReady = False
    devStatus = PCWU_STATUS_OFF
    devWaiting = PCWU_WAITING_NONE
    devProgram = PCWU_PROGRAM_NONE
    devError = PCWU_ERROR_NONE

    if 'IsManual' in mp and 'WaitingStatus' in mp and 'WaitingTimer' in mp:
        devReady = (
            mp['IsManual'] == 2                                         # Controller is on
            and
            (mp['WaitingStatus'] == 0 or mp['WaitingStatus'] == 2)      # Executive module is available for operation
            and
            mp['WaitingTimer'] == 0                                     # Heatpump is available for operation
        )

        # Determine waiting status
        if mp['WaitingStatus'] == 1:
            devWaiting = PCWU_WAITING_EXTOFF
        elif mp['WaitingStatus'] == 2:
            devWaiting = PCWU_WAITING_HPOFF
        elif mp['WaitingStatus'] == 32:
            devWaiting = PCWU_WAITING_STOP
        elif mp['WaitingStatus'] == 64:
            devWaiting = PCWU_WAITING_LOWCOP

        # Determine error status
        if mp['WaitingStatus'] == 4:
            devError = PCWU_ERROR_LOWPRES
        elif mp['WaitingStatus'] == 8:
            devError = PCWU_ERROR_HIGHPRES
        elif mp['WaitingStatus'] == 1024:
            devError = PCWU_ERROR_OVERTEMP
        else:
            devError = PCWU_ERROR_NONE

        # Determine device status
        if mp['IsManual'] != 2:
            devStatus = PCWU_STATUS_OFF
        elif devWaiting != PCWU_WAITING_NONE:
            devStatus = PCWU_STATUS_WAITING
        elif devError != PCWU_ERROR_NONE:
            devStatus = PCWU_STATUS_ERROR
        elif mp['HeatPumpON']:
            devStatus = PCWU_STATUS_RUNNING
        else:
            devStatus = PCWU_STATUS_IDLE

        # Determine device program
        if devStatus != PCWU_STATUS_RUNNING:
            devProgram = PCWU_PROGRAM_NONE
        elif mp['WaitingStatus'] == 16:
            devProgram = PCWU_PROGRAM_DEFROST
        elif mp['WaitingStatus'] == 128:
            devProgram = PCWU_PROGRAM_LOWTEMP
        elif mp['WaitingStatus'] == 256:
            devProgram = PCWU_PROGRAM_ANTIFREEZ
        elif mp['WaitingStatus'] == 512:
            devProgram = PCWU_PROGRAM_PREHEAT
        else:
            devProgram = PCWU_PROGRAM_HEAT

    return devReady, devStatus, devWaiting, devProgram, devError

def SetupDevice(unit, name, *args, **kwargs):
    if unit not in Devices:
        Domoticz.Device(Name=name, Unit=unit, *args, **kwargs).Create()
    return unit

def SetupDevicesPCWU(plugin):
    plugin.temp_devices = {
        'T1': SetupDevice(1, "T1 (ambient)", TypeName='Temperature'),
        'T2': SetupDevice(2, "T2 (tank bottom)", TypeName='Temperature'),
        'T3': SetupDevice(3, "T3 (tank top)", TypeName='Temperature'),
        'T4': SetupDevice(6, "T4 (solid fuel boiler)", TypeName='Temperature'),
        'T5': SetupDevice(7, "T5 (void)", TypeName='Temperature'),
        'T6': SetupDevice(8, "T6 (water inlet)", TypeName='Temperature'),
        'T7': SetupDevice(9, "T7 (water outlet)", TypeName='Temperature'),
        'T8': SetupDevice(10, "T8 (evaporator)", TypeName='Temperature'),
        'T9': SetupDevice(11, "T9 (before compressor)", TypeName='Temperature'),
        'T10': SetupDevice(12, "T10 (after compressor)", TypeName='Temperature'),
        'TapWaterTemp': SetupDevice( 5, "Tap Water Temp", Type=242, Subtype=1),
    }
    plugin.switch_devices = {
        'HeatPumpEnabled': SetupDevice(4, "Heatpump Enabled", TypeName='Switch', Image=9),
    }
    plugin.custom_devices = {
        'CompressorON - Count': SetupDevice(25, "CompressorON - Count", Type=243, Subtype=28, Switchtype=3, Options={"ValueQuantity" : "Count", "ValueUnits": ""}),
        'CompressorON - Time': SetupDevice(26, "CompressorON - Time", Type=243, Subtype=28, Switchtype=3, Options={"ValueQuantity" : "Time", "ValueUnits": "s"}),
        'EV1': SetupDevice(27, "EV1", TypeName="Custom", Options={"Custom": "1;"}),
        'Delta T': SetupDevice(28, "Delta T", TypeName="Custom", Options={"Custom": "1;°"}),
    }

def SetupExpertDevicesPCWU(plugin):

    plugin.x_switch_devices = {
        'AntiLegionellaEnabled': SetupDevice(13, "X - Anti Legionella Enabled", TypeName='Switch', Image=9),
        'AntiLegionellaUseHeaterE': SetupDevice(14, "X - Anti Legionella Use Heater E", TypeName='Switch', Image=9),
        'AntiLegionellaUseHeaterP': SetupDevice(15, "X - Anti Legionella Use Heater P", TypeName='Switch', Image=9),
        'AntiFreezingEnabled': SetupDevice(16, "X - Anti Freezing Enabled", TypeName='Switch', Image=9),
        'HeaterEEnabled': SetupDevice(17, "X - Heater E Enabled", TypeName='Switch', Image=9),
        'HeaterEBlocked': SetupDevice(18, "X - Heater E Blocked When HP ON", TypeName='Switch', Image=9),
        'HeaterPEnabled': SetupDevice(19, "X - Heater P Enabled", TypeName='Switch', Image=9),
        'HeaterPBlocked': SetupDevice(20, "X - Heater P Blocked When HP ON", TypeName='Switch', Image=9),
        'ExtControllerHPOFF': SetupDevice(21, "X - Ext. Controller HP OFF", TypeName='Switch', Image=9),
        'ExtControllerHeaterEOFF': SetupDevice(22, "X - Ext. Controller Heater E OFF", TypeName='Switch', Image=9),
        'ExtControllerHeaterPOFF': SetupDevice(23, "X - Ext. Controller Heater P OFF", TypeName='Switch', Image=9),
        'ExtControllerPumpFOFF': SetupDevice(24, "X - Ext. Controller Pump F OFF", TypeName='Switch', Image=9),
    }

    plugin.x_custom_devices = {
        'InstallationScheme': SetupDevice(29, "X - Installation Scheme", TypeName="Selector Switch", Image=11, Options={"LevelActions": "|||||||||", "LevelNames": "-|1|2|3|4|5|6|7|8|9", "LevelOffHidden": "true"}),
        'TapWaterSensor': SetupDevice(30, "X - Tap Water Sensor", TypeName="Selector Switch", Image=11, Options={"LevelActions": "||", "LevelNames": "T2|T3|T7"}),
        'WaterPumpOperationMode': SetupDevice(31, "X - Water Pump Operation Mode", TypeName="Selector Switch", Image=11, Options={"LevelActions": "|", "LevelNames": "Cont|Sync"}),
        'FanOperationMode': SetupDevice(32, "X - Fan Operation Mode", TypeName="Selector Switch", Image=11, Options={"LevelActions": "||", "LevelNames": "Max|Min|Day/Night"}),
    }

def SetupDevicesZPS(plugin):
    plugin.temp_devices = {
        'T1': SetupDevice(1, "T1 (collectors)", TypeName='Temperature'),
        'T2': SetupDevice(2, "T2 (tank bottom)", TypeName='Temperature'),
        'T3': SetupDevice(3, "T3 (air separator)", TypeName='Temperature'),
        'T4': SetupDevice(4, "T4 (tank top)", TypeName='Temperature'),
        'NightCoolingStartTemp': SetupDevice(9, "Night Cooling Start Temp", Type=242, Subtype=1),
        'NightCoolingStopTemp': SetupDevice(10, "Night Cooling Stop Temp", Type=242, Subtype=1),
        'CollectorPumpMaxTemp': SetupDevice(11, "Collector Pump Max Temp", Type=242, Subtype=1),
        'CollectorOverheatProtMaxTemp': SetupDevice(12, "Collector Overheat Protection Max Temp", Type=242, Subtype=1),
    }
    plugin.switch_devices = {
        'NightCoolingEnabled': SetupDevice(8, "Night Cooling Enabled", TypeName='Switch', Image=9),
        'CollectorOverheatProtEnabled': SetupDevice(13, "Collector Overheat Protection Enabled", TypeName='Switch', Image=9),
        'CollectorFreezingProtEnabled': SetupDevice(14, "Collector Freezing Protection Enabled", TypeName='Switch', Image=9),
        'TankOverheatProtEnabled': SetupDevice(15, "Tank Overheat Protection Enabled", TypeName='Switch', Image=9),
    }
    plugin.custom_devices = {
        'SWH kWh Total': SetupDevice(5, "SWH kWh Total", TypeName='Custom', Options={'Custom': '1;kWh'}),
        'SWH Generation': SetupDevice(6, "SWH Generation", TypeName='kWh', Switchtype=4),
        'SWH Consumption': SetupDevice(7, "SWH Consumption", TypeName='kWh', Options={'EnergyMeterMode':'1'}),
    }

def SetupExpertDevicesZPS(plugin):
    plugin.x_switch_devices = {
        'AlarmSoundEnabled': SetupDevice(16, "X - Alarm Sound Enabled", TypeName='Switch', Image=9),
        'KeySoundEnabled': SetupDevice(17, "X - Key Sound Enabled", TypeName='Switch', Image=9),
        'HolidayEnabled': SetupDevice(18, "X - Holiday Enabled", TypeName='Switch', Image=9),
        'PumpRegulationEnabled': SetupDevice(19, "X - Pump Regulation Enabled", TypeName='Switch', Image=9),
        'LegionellaProtEnabled': SetupDevice(20, "X - Legionella Protection Enabled", TypeName='Switch', Image=9),
        'PressureSwitchEnabled': SetupDevice(21, "X - Pressure Switch Enabled", TypeName='Switch', Image=9),
        'CirculationPumpEnabled': SetupDevice(22, "X - Circulation Pump Enabled", TypeName='Switch', Image=9),
    }
    plugin.x_custom_devices = {}

def SendCommand(plugin, command, *args, **kwargs):
    if plugin.baseUrl == None
        ser = plugin.serial_parameters.
        ser = serial.Serial(port=plugin.serialPort,baudrate=ser.baud_rate,bytesize=ser.byte_size,parity=ser.parity,stopbits=ser.stop_bits)
    else
        ser = serial.serial_for_url(plugin.baseUrl)
    dev = None

    if (plugin.devMode == 1) or (plugin.devMode == 2):
        dev = PCWU(plugin.conHardId, plugin.conSoftId, plugin.devHardId, plugin.devSoftId, plugin.onMessagePCWU)
    elif (plugin.devMode == 3):
        dev = ZPS(plugin.conHardId, plugin.conSoftId, plugin.devHardId, plugin.devSoftId, plugin.onMessageZPS)

    if dev:
        if (command == 'eavesDrop'):
            dev.eavesDrop(ser, 1, *args, **kwargs)
        else:
            command_method = getattr(dev, command)
            command_method(ser, *args, **kwargs)

    ser.close()

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def decode_serial_parameters(value):
    # Extracting parity (next digit)
    parity_mapping = {
        0: serial.PARITY_NONE,
        1: serial.PARITY_EVEN,
        2: serial.PARITY_ODD,
        3: serial.PARITY_MARK,
        4: serial.PARITY_SPACE
    }
    parity_value = value & 7
    parity = parity_mapping.get(parity_value, "Unknown")
    
    # Extracting stop bits (next digit)
    stop_bits_mapping = {
        0: serial.STOPBITS_ONE,
        8: serial.STOPBITS_ONE_POINT_FIVE,  # Will fall back to 2 on POSIX
        16: serial.STOPBITS_TWO
    }
    stop_bits_value = value & 24
    stop_bits = stop_bits_mapping.get(stop_bits_value, "Unknown")
    
    # Extracting byte size (last digit)
    byte_size_mapping = {
        0: serial.FIVEBITS,
        32: serial.SIXBITS,
        64: serial.SEVENBITS,
        96: serial.EIGHTBITS
    }
    byte_size_value = value & 96
    byte_size = byte_size_mapping.get(byte_size_value, "Unknown")

    # Extracting baud rate (first two digits)
    baud_rate = (value // 100) * 10 
    
    return {
        "baud_rate": baud_rate,
        "parity": parity,
        "stop_bits": stop_bits,
        "byte_size": byte_size
    }
