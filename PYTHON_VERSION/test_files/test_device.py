import amg88xx
# import FERB_client
import machine
import time

HOT_SPOT_SSID = 'teriyaki'
HOT_SPOT_PASS = 'Gy9BtTDx'
SERVER_IP = '10.42.0.1' # taken from ifconfig output
SERVER_PORT   = 12345

DEFAULT_ADDRESS = 0x69

SDA_ = machine.Pin(16)
SCL_ = machine.Pin(17)
I2C_ = machine.I2C(0, sda=SDA_, scl=SCL_, freq=400000)

SENSOR_ = amg88xx.AMG88XX(I2C_)
# NETWORK_ = FERB_client.network_handler(HOT_SPOT_SSID, HOT_SPOT_PASS, SERVER_IP, SERVER_PORT)

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


if __name__ == "__main__":
    _i2c_scan()

    while True:
        time.sleep(0.5)
        SENSOR_.refresh()
        # for row in range(8):
        #     print()
        #     for col in range(8):
        #         print('{:4d}'.format(SENSOR_[row, col]), end='')
        # print("\n\n------------------------------\n")

        print(SENSOR_._buf)

    # NETWORK_._get_networks()
    # NETWORK_._connect_wifi()
    # NETWORK_._connect_socket()
