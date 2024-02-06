import machine
import time

from amg88xx import AMG88XX  # Import the AMG88XX class from the amg88xx module
from FERB_client import NetHandler  # Import the NetHandler class from the FERB_client module

# Constants for network and server configuration
HOT_SPOT_SSID = 'teriyaki'
HOT_SPOT_PASS = 'Gy9BtTDx'
SERVER_IP = '10.42.0.1'     # IP address of the server, obtained from ifconfig output
SERVER_PORT = 12345         # Arbitrary port number for the server, ensure it's known and available

# I2C configuration for the Grid-EYE sensor
GRID_EYE_ADDR = 0x69        # I2C address of the Grid-EYE sensor
_SDA = machine.Pin(16)      # SDA pin for I2C communication
_SCL = machine.Pin(17)      # SCL pin for I2C communication
I2C_ = machine.I2C(0, sda=_SDA, scl=_SCL, freq=400000)  # Create an I2C instance

# Create instances of the AMG88XX class and NetHandler class
_SENSOR = AMG88XX(I2C_)     # Create an instance of the AMG88XX class for the Grid-EYE sensor
_FERB_NET = NetHandler(HOT_SPOT_SSID, HOT_SPOT_PASS, SERVER_IP, SERVER_PORT)  # Create an instance of the NetHandler class for network communication


def _search_for_i2c_device(addr) -> bool:
    """
    Scans for I2C devices and checks if the specified address corresponds to a device.

    Args:
        addr (int): The I2C address to search for.

    Returns:
        bool: True if the device is found, False otherwise.
    """
    devices = I2C_.scan()  # Scan for connected I2C devices

    if len(devices) != 0:
        print('Number of I2C devices found:', len(devices))
        if addr in devices:
            print(f"Device addr {hex(addr)} found. This is probably the Grid-EYE")
            return True
        else:
            print("Given device address not found...")
            for device in devices:
                print("Device on address: ", hex(device))
    else:
        print("No I2C devices found")

    return False


if __name__ == "__main__":
    if not _FERB_NET.connect_to_wifi():
        raise Exception(f"Could not connect to Wi-Fi network: {HOT_SPOT_SSID}")
    if not _FERB_NET.connect_to_socket():
        raise Exception(f"Could not connect to socket at {SERVER_IP}:{SERVER_PORT}")
    if not _search_for_i2c_device(GRID_EYE_ADDR):
        raise Exception("Grid-EYE sensor not found")

    # Main loop to continuously read sensor data and send it to the server
    while True:
        time.sleep_ms(350)  # Delay to control the sampling rate
        _SENSOR.refresh()   # Refresh the sensor data
        _FERB_NET.send_to_socket(_SENSOR._buf)  # Send the sensor data to the server
