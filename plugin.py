# Hewalex Python Plugin for Domoticz
#
# Authors: mvdklip
#
# Based on
#
# https://www.elektroda.pl/rtvforum/topic3499254.html
# https://github.com/aelias-eu/hewalex-geco-protocol

"""
<plugin key="Hewalex" name="Hewalex" author="mvdklip" version="0.6.0">
    <description>
        <h2>Hewalex Plugin</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Register boiler temperatures and more</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true"/>
        <param field="Port" label="Port" width="30px" required="true" default="8899"/>
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
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""


import serial
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

    devMode = None      # Operating mode of device (1 = PCWU - Eavesdropping, 2 = PCWU - Direct comms, 3 = ZPS - Direct comms)
    devReady = False    # Is device ready to accept commands?

    def __init__(self):
        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        else:
            Domoticz.Debugging(0)

        self.baseUrl = "socket://%s:%s" % (Parameters["Address"], Parameters["Port"])
        Domoticz.Debug("Base URL is set to %s" % self.baseUrl)

        self.devMode = int(Parameters["Mode2"])
        Domoticz.Debug("Device & Mode is set to %d" % self.devMode)

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
        if (self.devMode == 1) or (self.devMode == 2):
            if len(Devices) < 1:
                Domoticz.Device(Name="T1 (ambient)", Unit=1, TypeName='Temperature').Create()
            if len(Devices) < 2:
                Domoticz.Device(Name="T2 (tank bottom)", Unit=2, TypeName='Temperature').Create()
            if len(Devices) < 3:
                Domoticz.Device(Name="T3 (tank top)", Unit=3, TypeName='Temperature').Create()
            if len(Devices) < 4:
                Domoticz.Device(Name="Switch", Unit=4, TypeName='Switch', Image=9).Create()
            if len(Devices) < 5:
                Domoticz.Device(Name="Tap Water Temp", Unit=5, Type=242, Subtype=1).Create()
            if len(Devices) < 6:
                Domoticz.Device(Name="T4 (solid fuel boiler)", Unit=6, TypeName='Temperature').Create()
            if len(Devices) < 7:
                Domoticz.Device(Name="T5 (void)", Unit=7, TypeName='Temperature').Create()
            if len(Devices) < 8:
                Domoticz.Device(Name="T6 (water inlet)", Unit=8, TypeName='Temperature').Create()
            if len(Devices) < 9:
                Domoticz.Device(Name="T7 (water outlet)", Unit=9, TypeName='Temperature').Create()
            if len(Devices) < 10:
                Domoticz.Device(Name="T8 (evaporator)", Unit=10, TypeName='Temperature').Create()
            if len(Devices) < 11:
                Domoticz.Device(Name="T9 (before compressor)", Unit=11, TypeName='Temperature').Create()
            if len(Devices) < 12:
                Domoticz.Device(Name="T10 (after compressor)", Unit=12, TypeName='Temperature').Create()

        # ZPS devices
        elif (self.devMode == 3):
            if len(Devices) < 1:
                Domoticz.Device(Name="T1 (collectors)", Unit=1, TypeName='Temperature').Create()
            if len(Devices) < 2:
                Domoticz.Device(Name="T2 (tank bottom)", Unit=2, TypeName='Temperature').Create()
            if len(Devices) < 3:
                Domoticz.Device(Name="T3 (air separator)", Unit=3, TypeName='Temperature').Create()
            if len(Devices) < 4:
                Domoticz.Device(Name="T4 (tank top)", Unit=4, TypeName='Temperature').Create()
            if len(Devices) < 5:
                Domoticz.Device(Name="SWH kWh Total", Unit=5, TypeName='Custom', Options={'Custom': '1;kWh'}).Create()
            if len(Devices) < 6:
                Domoticz.Device(Name="SWH Generation", Unit=6, TypeName='kWh', Switchtype=4).Create()
            if len(Devices) < 7:
                Domoticz.Device(Name="SWH Consumption", Unit=7, TypeName='kWh', Options={'EnergyMeterMode':'1'}).Create()
            if len(Devices) < 8:
                Domoticz.Device(Name="Night Cooling Enabled", Unit=8, TypeName='Switch', Image=9).Create()
            if len(Devices) < 9:
                Domoticz.Device(Name="Night Cooling Start Temp", Unit=9, Type=242, Subtype=1).Create()
            if len(Devices) < 10:
                Domoticz.Device(Name="Night Cooling Stop Temp", Unit=10, Type=242, Subtype=1).Create()
            if len(Devices) < 11:
                Domoticz.Device(Name="Collector Pump Max Temp", Unit=11, Type=242, Subtype=1).Create()
            if len(Devices) < 12:
                Domoticz.Device(Name="Collector Overheat Protection Max Temp", Unit=12, Type=242, Subtype=1).Create()

        DumpConfigToLog()

        Domoticz.Heartbeat(5)

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onMessagePCWU(self, dev, h, sh, m):
        Domoticz.Debug("onMessagePCWU called")
        if (self.devMode == 1 and sh["FNC"] == 0x60) or (self.devMode == 2 and sh["FNC"] == 0x50):
            mp = dev.parseRegisters(sh["RestMessage"], sh["RegStart"], sh["RegLen"])
            if 'T1' in mp:
                Devices[1].Update(nValue=0, sValue=str(mp['T1']))
            if 'T2' in mp:
                Devices[2].Update(nValue=0, sValue=str(mp['T2']))
            if 'T3' in mp:
                Devices[3].Update(nValue=0, sValue=str(mp['T3']))
            if 'T4' in mp:
                Devices[6].Update(nValue=0, sValue=str(mp['T4']))
            if 'T5' in mp:
                Devices[7].Update(nValue=0, sValue=str(mp['T5']))
            if 'T6' in mp:
                Devices[8].Update(nValue=0, sValue=str(mp['T6']))
            if 'T7' in mp:
                Devices[9].Update(nValue=0, sValue=str(mp['T7']))
            if 'T8' in mp:
                Devices[10].Update(nValue=0, sValue=str(mp['T8']))
            if 'T9' in mp:
                Devices[11].Update(nValue=0, sValue=str(mp['T9']))
            if 'T10' in mp:
                Devices[12].Update(nValue=0, sValue=str(mp['T10']))
            if 'TapWaterTemp' in mp:
                Devices[5].Update(nValue=0, sValue=str(mp['TapWaterTemp']))
            if self.devMode == 1:
                if 'WaitingStatus' in mp:
                    newValue = int(mp['WaitingStatus'] == 0)
                    if newValue != Devices[4].nValue:
                        Devices[4].Update(nValue=newValue, sValue="")
                self.devReady = False
            elif self.devMode == 2:
                if 'HeatPumpEnabled' in mp:
                    newValue = int(mp['HeatPumpEnabled'])
                    if newValue != Devices[4].nValue:
                        Devices[4].Update(nValue=newValue, sValue="")
                if ('IsManual' in mp and 'WaitingStatus' in mp and 'WaitingTimer' in mp):
                    self.devReady = (
                        mp['IsManual'] == 2
                        and
                        (mp['WaitingStatus'] == 0 or mp['WaitingStatus'] == 2)
                        and
                        mp['WaitingTimer'] == 0
                    )

    def onMessageZPS(self, dev, h, sh, m):
        Domoticz.Debug("onMessageZPS called")
        if (sh["FNC"] == 0x50):
            mp = dev.parseRegisters(sh["RestMessage"], sh["RegStart"], sh["RegLen"])
            if 'T1' in mp:
                Devices[1].Update(nValue=0, sValue=str(mp['T1']))
            if 'T2' in mp:
                Devices[2].Update(nValue=0, sValue=str(mp['T2']))
            if 'T3' in mp:
                Devices[3].Update(nValue=0, sValue=str(mp['T3']))
            if 'T4' in mp:
                Devices[4].Update(nValue=0, sValue=str(mp['T4']))
            if 'TotalEnergy' in mp:
                Devices[5].Update(nValue=0, sValue=str(mp['TotalEnergy']))
                if 'CollectorPower' in mp:
                    Devices[6].Update(nValue=0, sValue=str(mp['CollectorPower'])+";"+str(mp['TotalEnergy'] * 1000))
            if 'Consumption' in mp:
                Devices[7].Update(nValue=0, sValue=str(mp['Consumption'])+";0")
            if 'NightCoolingEnabled' in mp:
                newValue = int(mp['NightCoolingEnabled'])
                if newValue != Devices[8].nValue:
                    Devices[8].Update(nValue=newValue, sValue="")
            if 'NightCoolingStartTemp' in mp:
                Devices[9].Update(nValue=0, sValue=str(mp['NightCoolingStartTemp']))
            if 'NightCoolingStopTemp' in mp:
                Devices[10].Update(nValue=0, sValue=str(mp['NightCoolingStopTemp']))
            if 'CollectorPumpMaxTemp' in mp:
                Devices[11].Update(nValue=0, sValue=str(mp['CollectorPumpMaxTemp']))
            if 'CollectorOverheatProtMaxTemp' in mp:
                Devices[12].Update(nValue=0, sValue=str(mp['CollectorOverheatProtMaxTemp']))
            if self.devMode == 3:
                self.devReady = True

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for unit %d with command %s, level %s." % (Unit, Command, Level))

        if self.devReady:

            # PCWU commands
            if (self.devMode == 2):
                if (Unit == 4) and (Command == "On"):
                    SendCommand(self, 'enable')
                    Devices[Unit].Update(nValue=1, sValue="")
                elif (Unit == 4) and (Command == "Off"):
                    SendCommand(self, 'disable')
                    Devices[Unit].Update(nValue=0, sValue="")
                elif (Unit == 5) and (Command == "Set Level"):
                    SendCommand(self, 'setTapWaterTemp', Level)
                    Devices[Unit].Update(nValue=0, sValue=str(Level))

            # ZPS commands
            elif (self.devMode == 3):
                if (Unit == 8) and (Command == "On"):
                    SendCommand(self, 'enableNightCooling')
                    Devices[Unit].Update(nValue=1, sValue="")
                elif (Unit == 8) and (Command == "Off"):
                    SendCommand(self, 'disableNightCooling')
                    Devices[Unit].Update(nValue=0, sValue="")
                elif (Unit == 9) and (Command == "Set Level"):
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
def SendCommand(plugin, command, *args, **kwargs):
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
