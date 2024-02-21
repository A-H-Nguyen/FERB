import machine
import time

from amg88xx import AMG88XX        # Import the AMG88XX class
from ClientNethandler import NetHandler  # Import the NetHandler class

class Ferb:
    def __init__(self, _ssid, _pass, _ip, _port, _grid_eye_addr, _sda, _scl) -> None:
        self._SSID = _ssid
        self._PASS = _pass
        self._IP = _ip
        self._PORT = _port

        self._GRID_EYE_ADDR = _grid_eye_addr
        self._SDA = machine.Pin(_sda)
        self._SCL = machine.Pin(_scl)
        self._I2C_BUS = machine.I2C(0, sda=self._SDA, scl=self._SCL, freq=400000)

        self._NET = NetHandler(self._SSID, self._PASS, self._IP, self._PORT)
        self._SENSOR = AMG88XX(self._I2C_BUS)

        self._LED = machine.Pin("LED", machine.Pin.OUT)

    def connect_to_wifi(self) -> str: #bool:
        return self._NET.connect_to_wifi()
    
    def connect_to_socket(self) -> bool:
        return self._NET.connect_to_socket()

    def search_for_i2c_device(self, addr) -> bool:
        """
        Scans for I2C devices and checks if the specified address corresponds to a device.

        Args:
            addr (int): The I2C address to search for.

        Returns:
            bool: True if the device is found, False otherwise.
        """
        devices = self._I2C_BUS.scan()  # Scan for connected I2C devices

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

    def read_temps(self) -> bytearray:
        """
        Read temps from Grid-EYE
        :return:
        """
        # time.sleep_ms(200)
        self._SENSOR.refresh()
        time.sleep_ms(100)
        return self._SENSOR.get_buf()

    def print_temps(self, data: bytearray):
        """
        Print Grid-EYE temps to serial for debugging
        :return:
        """
        for i in range(0, len(data), 2):
            pixel_value = data[i] | (data[i + 1] << 8)
            print(pixel_value, end=' ')
            if (i + 2) % 16 == 0:
                print()

    def send_temps(self, data: bytearray):
        """
        Send temps to socket
        :return:
        """
        self._NET.send_to_socket(data)
        time.sleep_ms(250)

    def led_high(self):
        self._LED.high()

    def led_low(self):
        self._LED.low()
