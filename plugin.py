# Hewalex Python Plugin for Domoticz
#
# Authors: mvdklip
#
# Based on
#
# https://www.elektroda.pl/rtvforum/topic3499254.html
# https://github.com/mvdklip/hewalex-geco-protocol

"""
<plugin key="Hewalex" name="Hewalex" author="mvdklip" version="0.1.0">
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
        <param field="Mode3" label="Query interval" width="75px" required="true">
            <options>
                <option label="15 sec" value="3"/>
                <option label="30 sec" value="6"/>
                <option label="1 min" value="12"/>
                <option label="3 min" value="36"/>
                <option label="5 min" value="60" default="true"/>
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

from hewalex_geco.devices import PCWU


class BasePlugin:
    enabled = False
    lastPolled = 0
    baseUrl = None
    maxAttempts = 3

    # Controller (Master)
    conHardId = 1
    conSoftId = 1

    # PCWU (Slave)
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

        if len(Devices) < 1:
            Domoticz.Device(Name="PCWU T1 (ambient)", Unit=1, TypeName='Temperature').Create()
        if len(Devices) < 2:
            Domoticz.Device(Name="PCWU T2 (tank bottom)", Unit=2, TypeName='Temperature').Create()
        if len(Devices) < 3:
            Domoticz.Device(Name="PCWU T3 (tank top)", Unit=3, TypeName='Temperature').Create()

        DumpConfigToLog()

        self.baseUrl = "socket://%s:%s" % (Parameters["Address"], Parameters["Port"])
        Domoticz.Debug("Base URL is set to %s" % self.baseUrl)

        Domoticz.Heartbeat(5)

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onMessagePCWU(self, obj, h, sh, m):
        Domoticz.Debug("onMessagePCWU called")
        if sh["FNC"] == 0x60:
            mp = obj.parseX60RestMessage(sh["RestMessage"])
            Devices[1].Update(nValue=0, sValue=str(mp['T1']))
            Devices[2].Update(nValue=0, sValue=str(mp['T2']))
            Devices[3].Update(nValue=0, sValue=str(mp['T3']))

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
                    ser = serial.serial_for_url(self.baseUrl)
                    pcwu = PCWU(self.conHardId, self.conSoftId, self.devHardId, self.devSoftId, self.onMessagePCWU)
                    pcwu.eavesDrop(ser, 1)
                    ser.close()
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


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


# Generic helper functions
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
