import machine
import network
import time

# from machine import Pin
from umqttsimple import MQTTClient

_HOT_SPOT_SSID = 'teriyaki'
_HOT_SPOT_PASS = '5kn3WdFp'
# _SERVER_IP = '127.0.1.1'
# _SERVER_PORT = 12345

MQTT_SERVER = 'broker.hivemq.com'
CLIENT_ID = 'bigles'
TOPIC_PUB = b'TomsHardware'
TOPIC_MSG = b'Movement Detected'


def mqtt_connect():
    client = MQTTClient(CLIENT_ID, MQTT_SERVER, keepalive=3600)
    client.connect()
    print('Connected to %s MQTT Broker'%(MQTT_SERVER))
    return client

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    # machine.reset()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
_wlan_connected = False
while not _wlan_connected:
    print(f"Attempting to connect to {_HOT_SPOT_SSID}...\n")
    wlan.connect(ssid=_HOT_SPOT_SSID, key=_HOT_SPOT_PASS)
    time.sleep(3)
    if wlan.isconnected():
        _wlan_connected = True
print(f"Connected to network on {_HOT_SPOT_SSID}")

while True:
    try:
        client = mqtt_connect()

        client.publish(TOPIC_PUB, TOPIC_MSG)
        time.sleep(3)

    except OSError as e:
        reconnect()

