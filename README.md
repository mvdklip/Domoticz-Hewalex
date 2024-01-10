# Domoticz-Hewalex
Domoticz plugin to integrate Hewalex heat and solar pumps

Tested with Python version 3.8, Domoticz versions 2020.2 and 2021.1

## Prerequisites

### Heat pumps (PCWU)

RS485 to USB or Wi-Fi device setup and either eavesdropping on the communication between the G-426 controller and the PCWU or communicating directly to the PCWU over a dedicated RS485 port. Eavesdropping is easier to setup and allows reading temperatures but does not allow control over the pump. See https://github.com/mvdklip/hewalex-geco-protocol/tree/main/docs/PCWU for more information.

### Solar pumps (ZPS)

RS485 to USB or Wi-Fi device setup and connected to the RS485 port on the backside of the G-422 controller. https://github.com/mvdklip/hewalex-geco-protocol/tree/main/docs/ZPS for more information.

## Installation

Assuming that domoticz directory is installed in your home directory.

```bash
cd ~/domoticz/plugins
git clone https://github.com/mvdklip/Domoticz-Hewalex
# restart domoticz:
sudo /etc/init.d/domoticz.sh restart
```
In the web UI, navigate to the Hardware page and add an entry of type "Hewalex".

Make sure to (temporarily) enable 'Accept new Hardware Devices' in System Settings so that the plugin can add devices.

Afterwards navigate to the Devices page and enable the newly created devices.

## Expert mode

Please enable expert mode only if you:
A) Are absolutely sure that you know all ins and outs of your Hewalex device.
B) Identified some 'X' device in the sourcecode of the plugin you cannot live without.

You are SOLELY responsible for the consequences of enabling expert mode and interacting with the 'X' devices created. Curiosity killed the cat!

Also note the known issue below - there is no easy way to delete 'X' devices afterwards. You'll have to delete them manually one by one.

## Known issues

Disabling expert mode will not delete previously created 'X' devices.

## Updating

Like other plugins, in the Domoticz-Hewalex directory:
```bash
git pull
sudo /etc/init.d/domoticz.sh restart
```

## Parameters

| Parameter | Value |
| :--- | :--- |
| **Serial Port or IP address** | Serial port device or IP of the RS485 to Wi-Fi device eg. /dev/ttyUSB0 or 192.168.1.231 |
| **Port** | Port of the RS485 to Wi-Fi device eg. 8899; Set to zero for serial port device |
| **Serial parameters** | Comma separated serial parameters eg. 38400,8,N,1 |
| **Device & Mode** | Device type and mode of communication |
| **Query interval** | How often is data retrieved |
| **Controller and device Ids** | Controller and device hard and soft ids eg. 1,1;2,2 |
| **Expert mode** | Enable expert mode - RTFM before enabling! |
| **Debug log** | Show debug logging |

## Acknowledgements

Based on

https://www.elektroda.pl/rtvforum/topic3499254.html \
https://github.com/aelias-eu/hewalex-geco-protocol
