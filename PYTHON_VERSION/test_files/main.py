# DEPRECATE THIS FILE - DON'T NEED IT ANYMORE

import amg88xx
import machine
import network
import usocket as socket
import uselect as select
import time
# import urequests

HOT_SPOT_SSID = 'teriyaki'
HOT_SPOT_PASS = 'Gy9BtTDx'
SERVER_IP = '10.42.0.1' # taken from ifconfig output
SERVER_PORT   = 12345

DEFAULT_ADDRESS = 0x69

SDA_ = machine.Pin(16)
SCL_ = machine.Pin(17)
I2C_ = machine.I2C(0, sda=SDA_, scl=SCL_, freq=400000)

_SENSOR = amg88xx.AMG88XX(I2C_)

wlan = network.WLAN(network.STA_IF)  # Use network.STA_IF for station mode
wlan.active(True)

# Use 'WPA-EAP' for WPA2 Enterprise authentication
# wlan.connect(ssid='NUwave', auth=(network.WLAN.WPA2_EAP,'ha.je','password'), key_mgmt='WPA-EAP')
# ssid = 'NUwave-guest'
# wlan.connect(ssid=ssid)

def _i2c_scan(addr=DEFAULT_ADDRESS) -> None:
    devices = I2C_.scan()

    if len(devices) != 0:
        print('Number of I2C devices found:',len(devices))
        if addr in devices:
            print(f"Device addr {hex(addr)} found. This is probably the Grid-EYE")
        else:
            print("Given device address not found:")
            for device in devices:
                print("Device Hexadecimel Address = ",hex(device))
    else:
        raise Exception("No i2c devices found")


def print_nets():
    nets = wlan.scan()  # List with tuples (ssid, bssid, channel, RSSI, security, hidden)
    print(f"Not connected...\n" +
          f"\n-------------------------------------\n" +
          f"Available networks:")
    for net in nets:
        # Access the 0th element of the tuple for SSID
        # Access the 3rd element of the tuple for RSSI
        print(f"SSID: {net[0]}, RSSI: {net[3]}")
    print(f"\n-------------------------------------\n")


_wlan_connected = False
while not _wlan_connected:
    print(f"Attempting to connect to {HOT_SPOT_SSID}...\n")
    wlan.connect(ssid=HOT_SPOT_SSID, key=HOT_SPOT_PASS)
    time.sleep(5)

    if wlan.isconnected():
        _wlan_connected = True

print(f"Connected to network on {HOT_SPOT_SSID}")

_socket = socket.socket()
_socket_connected = False
while not _socket_connected:
    try:
        _socket.connect((SERVER_IP, SERVER_PORT))
        _socket_connected = True
        print(f"Connected to server at {(SERVER_IP, SERVER_PORT)}")

    except Exception as e:
        print(f"Connection failed: {e}")
        time.sleep(3)

# # Virtual Handshake to verify that server has been connected to:
# _socket.sendall(b"Hello From FERB Unit")
# time.sleep_ms(500)

# data = _socket.recv(1024)
# time.sleep_ms(500)

# if data != "ACK":
#     raise Exception(f"Error: could not connect to host on {SERVER_IP}")

print("Begin running Grid-EYE routine...\n")

_i2c_scan()
while True:
    time.sleep_ms(350)
    _SENSOR.refresh()
    _socket.sendall(_SENSOR._buf)

