print("Starting Hewalex 2 Mqtt")

import os
import threading
import configparser
import serial
from hewalex_geco.devices import PCWU, ZPS
import paho.mqtt.client as mqtt

# polling interval
get_status_interval = 15.0

# Controller (Master)
conHardId = 1
conSoftId = 1

# ZPS (Slave)
devHardId = 2
devSoftId = 2

# Read Configs
def initConfiguration():
    print("reading config")
    config_file = os.path.join(os.path.dirname(__file__), 'hewalex2mqttconfig.ini')
    config = configparser.ConfigParser()
    config.read(config_file)
    # Mqtt
    global _MQTT_ip
    if (os.getenv('MQTT_ip') != None):        
        _MQTT_ip = os.getenv('MQTT_ip')
    else:
        _MQTT_ip = config['MQTT']['MQTT_ip']
    global _MQTT_port
    if (os.getenv('MQTT_port') != None):        
        _MQTT_port = int(os.getenv('MQTT_port'))
    else:
        _MQTT_port = config.getint('MQTT', 'MQTT_port')
    global _MQTT_authentication
    if (os.getenv('MQTT_authentication') != None):        
        _MQTT_authentication = os.getenv('MQTT_authentication') == "True"
    else:
        _MQTT_authentication = config.getboolean('MQTT','MQTT_authentication')
    global _MQTT_user
    if (os.getenv('MQTT_user') != None):        
        _MQTT_user = os.getenv('MQTT_user')
    else:
        _MQTT_user = config['MQTT']['MQTT_user']
    global _MQTT_pass
    if (os.getenv('MQTT_pass') != None):        
        _MQTT_pass = os.getenv('MQTT_pass')
    else:
        _MQTT_pass = config['MQTT']['MQTT_pass']
    global _Device_Zps_Enabled
    if (os.getenv('Device_Zps_Enabled') != None):        
        _Device_Zps_Enabled = os.getenv('Device_Zps_Enabled') == "True"
    else:
        _Device_Zps_Enabled = config.getboolean('ZPS', 'Device_Zps_Enabled')
    
    # ZPS Device
    global _Device_Zps_Address
    if (os.getenv('_Device_Zps_Address') != None):        
        _Device_Zps_Address = os.getenv('Device_Zps_Address')
    else:
        _Device_Zps_Address = config['ZPS']['Device_Zps_Address']
    global _Device_Zps_Port
    if (os.getenv('Device_Zps_Port') != None):        
        _Device_Zps_Port = os.getenv('Device_Zps_Port')
    else:
        _Device_Zps_Port = config['ZPS']['Device_Zps_Port']

    global _Device_Zps_MqttTopic
    if (os.getenv('Device_Zps_MqttTopic') != None):        
        _Device_Zps_MqttTopic = os.getenv('Device_Zps_MqttTopic')
    else:
        _Device_Zps_MqttTopic = config['ZPS']['Device_Zps_MqttTopic']

def start_mqtt():
    global client
    print('Connection in progress to the Mqtt broker (IP:' +_MQTT_ip + ' PORT:'+str(_MQTT_port)+')')
    client = mqtt.Client()
    if _MQTT_authentication:
        print('Mqtt authentication enabled')
        client.username_pw_set(username=_MQTT_user, password=_MQTT_pass)
    client.on_connect = on_connect_mqtt
    #client.on_message = on_message_mqtt
    client.connect(_MQTT_ip, _MQTT_port)
    client.loop_start()    

def on_connect_mqtt(client, userdata, flags, rc):
    print("Mqtt: Connected to broker. ")

# onMessage handler
def onMessage(obj, h, sh, m):    
    if sh["FNC"] == 0x50:
        #obj.printMessage(h, sh)
        mp = obj.parseRegisters(sh["RestMessage"], sh["RegStart"], sh["RegLen"])
        for item in mp.items():
            print(_Device_Zps_MqttTopic + "/" + item[0])
            client.publish(_Device_Zps_MqttTopic + "/" + item[0], item[1])
                        

def device_readregisters_enqueue():
    """Get device status every x seconds"""
    threading.Timer(get_status_interval, device_readregisters_enqueue).start()
    if _Device_Zps_Enabled:        
        readZPS()

def readZPS():
    ser = serial.serial_for_url("socket://%s:%s" % (_Device_Zps_Address, _Device_Zps_Port))
    dev = ZPS(conHardId, conSoftId, devHardId, devSoftId, onMessage)        
    dev.readStatusRegisters(ser)
    ser.close()

if __name__ == "__main__":
    initConfiguration()
    start_mqtt()
    device_readregisters_enqueue()
