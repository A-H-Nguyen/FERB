import machine
import time

from amg88xx import AMG88XX
from amg88xx import _PIXEL_TEMP_CONVERSION
from ClientNethandler import NetHandler
from debug import FerbCLI

# Constants for network and server configuration
HOST_SSID = 'Ferbius'
HOST_PASS = 'ajetaFERB'
SERVER_IP = '10.42.0.1'  # IP address of the server, obtained from ifconfig output
SERVER_PORT = 12345      # Arbitrary port number for the server, ensure it's known and available

# Constants for Grid-EYE configuration
SDA_PIN = 16
SCL_PIN = 17

debug_pin = machine.Pin(12, machine.Pin.IN)
led = machine.Pin("LED", machine.Pin.OUT)

if __name__ == "__main__":

    net = NetHandler()
    sensor = AMG88XX(machine.I2C(0, sda=SDA_PIN, scl=SCL_PIN, freq=400000))
    
    if debug_pin.value() > 0:
        print("FERB booting in Debug mode...\n")
        debug_mode = True
    else:
        debug_mode = False

    try:
        if debug_mode:
            cli = FerbCLI(sensor=sensor, nethandler=net)
        
        else:
            print("Check wi-fi connection:")
            if not net.is_wifi_connected():
                if not net.connect_to_wifi(HOST_SSID, HOST_PASS):
                    raise Exception(f"Could not connect to wi-fi on {HOST_SSID}")
            print(f"Connected to wi-fi on {net.get_ssid()}")

            net.connect_to_socket(SERVER_IP, SERVER_PORT)

        while True:
            if debug_mode:
                if not cli.handle_input():
                    break
            else:
                try:
                    sensor.refresh()
                    time.sleep_ms(100)

                    # for row in range(8):
                    #     print()
                    #     for col in range(8):
                    #         print('{:4d}'.format(sensor[row, col]), end='')
                    # print()

                    data = sensor.get_buf()
                    total = 0
                    for i in range(0, 128, 2):
                        total += data[i] | (data[i + 1] << 8)
                    average = (total / 64) * _PIXEL_TEMP_CONVERSION

                    print(f"Average temp is {average} C\n")

                    if average > 25.0:
                        led.on()
                        net.send_to_socket(bytearray(str(average).encode()))
                        time.sleep_ms(200)
                    else:
                        led.off()

                except Exception as e:
                    break

    except Exception as e:
        machine.reset()

    except KeyboardInterrupt as k:
        net.disconnect_socket()
        time.sleep_ms(200)
        
        net.disconnect_wifi()
        time.sleep_ms(200)

        print("Ok, bye")
