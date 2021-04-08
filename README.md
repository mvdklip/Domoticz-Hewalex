# Domoticz-Hewalex
Domoticz plugin to integrate Hewalex solar and heat pumps

Tested with Python version 3.8, Domoticz version 2020.2 stable

## Prerequisites

### Solar pumps (ZPS)

Not implemented yet.

### Heat pumps (PCWU)

RS485 to Wi-Fi device setup and either eavesdropping on the communication between the G-426 controller and the PCWU or communicating directly to the PCWU over a dedicated RS485 port. See https://github.com/mvdklip/hewalex-geco-protocol/tree/main/docs/PCWU for more information.

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

## Known issues

This plugin is work in progress. Currently it only reads temperature registers for heat pumps. In the future it will also support solar pumps and allow control over the connected pump.

## Updating

Like other plugins, in the Domoticz-Hewalex directory:
```bash
git pull
sudo /etc/init.d/domoticz.sh restart
```

## Parameters

| Parameter | Value |
| :--- | :--- |
| **IP address** | IP of the RS485 to Wi-Fi device eg. 192.168.1.231 |
| **Port** | Port of the RS485 to Wi-Fi device eg. 8899 |
| **PCWU Mode** | Eavesdropping or Direct comms |
| **Query interval** | how often is data retrieved |
| **Debug** | show debug logging |

## Acknowledgements

Based on

https://www.elektroda.pl/rtvforum/topic3499254.html \
https://github.com/mvdklip/hewalex-geco-protocol
