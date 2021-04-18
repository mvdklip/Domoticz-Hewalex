# Hewalex Python Plugin for Domoticz
#
# Authors: mvdklip
#
# Based on
#
# https://www.elektroda.pl/rtvforum/topic3499254.html
# https://github.com/aelias-eu/hewalex-geco-protocol

"""
<plugin key="Hewalex" name="Hewalex" author="mvdklip" version="0.5.0">
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
    devMode = None

    # Controller (Master)
    conHardId = 1
    conSoftId = 1

    # Device (Slave)
    devHardId = 2
    devSoftId = 2

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

        if (self.devMode == 1) or (self.devMode == 2):
            if len(Devices) < 1:
                Domoticz.Device(Name="T1 (ambient)", Unit=1, TypeName='Temperature').Create()
            if len(Devices) < 2:
                Domoticz.Device(Name="T2 (tank bottom)", Unit=2, TypeName='Temperature').Create()
            if len(Devices) < 3:
                Domoticz.Device(Name="T3 (tank top)", Unit=3, TypeName='Temperature').Create()
            if len(Devices) < 4:
                Domoticz.Device(Name="Switch", Unit=4, TypeName='Switch', Image=9).Create()
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
                Domoticz.Device(Name="SWH kWh total", Unit=5, TypeName='Custom', Options={'Custom': '1;kWh'}).Create()
            if len(Devices) < 6:
                Domoticz.Device(Name="SWH generation", Unit=6, TypeName='kWh', Switchtype=4).Create()
            if len(Devices) < 7:
                Domoticz.Device(Name="Consumption", Unit=7, TypeName='kWh', Options={'EnergyMeterMode':'1'}).Create()

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
            if 'WaitingStatus' in mp:
                newValue = int(mp['WaitingStatus'] != 2)
                if newValue != Devices[4].nValue:
                    Devices[4].Update(nValue=newValue, sValue="")

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

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for unit %d with command %s, level %s." % (Unit, Command, Level))
        if (Unit == 4) and (Command == "On") and (self.devMode == 2):
            SendCommand(self, 'enable')
            Devices[Unit].Update(nValue=1, sValue="")   # TODO - check if device is actually switched on
        elif (Unit == 4) and (Command == "Off") and (self.devMode == 2):
            SendCommand(self, 'disable')                # TODO - ... or off
            Devices[Unit].Update(nValue=0, sValue="")
        return True

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called %d" % self.lastPolled)

        if self.lastPolled == 0:
            attempt = 1

            while True:
                if 1 < attempt < self.maxAttempts:
                    Domoticz.Debug("Previous attempt failed, trying again...")
                if attempt >= self.maxAttempts:
                    Domoticz.Error("Failed to retrieve data from %s, cancelling..." % self.baseUrl)
                    break
                attempt += 1

                try:
                    if (self.devMode == 1):
                        SendCommand(self, 'eavesDrop')
                    elif (self.devMode == 2) or (self.devMode == 3):
                        SendCommand(self, 'readStatusRegisters')
                except Exception as e:
                    Domoticz.Log("Exception from %s; %s" % (self.baseUrl, e))
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
def SendCommand(plugin, command):
    ser = serial.serial_for_url(plugin.baseUrl)
    dev = None

    if (plugin.devMode == 1) or (plugin.devMode == 2):
        dev = PCWU(plugin.conHardId, plugin.conSoftId, plugin.devHardId, plugin.devSoftId, plugin.onMessagePCWU)
    elif (plugin.devMode == 3):
        dev = ZPS(plugin.conHardId, plugin.conSoftId, plugin.devHardId, plugin.devSoftId, plugin.onMessageZPS)

    if dev:
        if (command == 'eavesDrop'):
            dev.eavesDrop(ser, 1)
        elif (command == 'readStatusRegisters'):
            dev.readStatusRegisters(ser)
        elif (command == 'disable'):
            dev.disable(ser)
        elif (command == 'enable'):
            dev.enable(ser)

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
