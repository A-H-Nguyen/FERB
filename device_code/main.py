import machine
import time

from amg88xx import AMG88XX, _PIXEL_TEMP_CONVERSION
from ClientNethandler import NetHandler
from debug import FerbCLI

# Constants for network and server configuration
HOST_SSID = 'Ferbius'
HOST_PASS = 'ajetaFERB'
SERVER_IP = '10.42.0.1'  # IP address of the server, obtained from ifconfig output
SERVER_PORT = 11111     # Arbitrary port number for the server, ensure it's known and available

# Constants for Grid-EYE configuration
SDA_PIN = 16
SCL_PIN = 17

debug_pin = machine.Pin(22, machine.Pin.IN)
led = machine.Pin("LED", machine.Pin.OUT)

<<<<<<< Updated upstream
net = NetHandler()
sensor = AMG88XX(machine.I2C(0, sda=SDA_PIN, scl=SCL_PIN, freq=400000))
=======

def calibrate_sensor(sensor, calibration_time=5):
    print("Calibrating sensor for environmental temperature...")

    total_pixel_values = 64
    total = 0

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < calibration_time * 1000:
        sensor.refresh()
        time.sleep_ms(1000)  # Adjust the sleep time if needed
        pixels = sensor.get_buf()

        for i in range(0, 128, 2):
            total += pixels[i] | (pixels[i + 1] << 8)

    average = (total / (total_pixel_values * calibration_time)) * _PIXEL_TEMP_CONVERSION

    print(f"Enviromental temperature is {average} C")
    print("Calibration Complete\n")

    return average


if __name__ == "__main__":
>>>>>>> Stashed changes


def get_average_temp(data) -> float:
    total = sum(data[i] | (data[i + 1] << 8) for i in range(0, 128, 2))
    average = (total / 64) * _PIXEL_TEMP_CONVERSION
    # print(f"Average temp is {average} C\n")
    return average


def print_grid_eye(grid_eye: AMG88XX):
    for row in range(8):
        print()
        for col in range(8):
            print('{:4d}'.format(sensor[row, col]), end='')
    print("\n-------------------------")


def FERB_debug():
    print("FERB booting in Debug mode...\n")
    cli = FerbCLI(sensor=sensor, nethandler=net)
    while True:
        if not cli.handle_input():
            break    


def FERB_main():
    if not net.is_wifi_connected():
        print(f"Attempting to connect to {HOST_SSID} ...")
        if not net.connect_to_wifi(10, HOST_SSID, HOST_PASS):
            raise Exception(f"Could not connect to wi-fi on {HOST_SSID}")
    print(f"Successfully connected to {net.get_ssid()}\n")
    print(f"Attempting to connect to socket {SERVER_IP}:{SERVER_PORT} ...")
    
    net.connect_to_socket(SERVER_IP, SERVER_PORT)
    
    print(f"Socket connection successful\n")

    while True:
        try:
            sensor.refresh() # Grid-EYE read data
            time.sleep_ms(100)
            # print_grid_eye(sensor)
            net.send_to_socket(sensor.get_buf())

        # Change this later -- we want it so that if something fucks up the FERB will try
        # reconnecting to the wi-fi and then the socket server
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

        except KeyboardInterrupt as k:
            net.disconnect_socket()
            time.sleep_ms(200)
            
            net.disconnect_wifi()
            time.sleep_ms(200)

            print("Ok, bye")

            led.off()
            
            break


if __name__ == "__main__":
    led.on()

    if debug_pin.value() < 1:
        FERB_debug()    
    else:
<<<<<<< Updated upstream
        FERB_main()
=======
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

        enviro = calibrate_sensor(sensor)
        while True:
            if debug_mode:
                # if not cli.handle_input():
                #     break
                pass
            else:
                try:
                    sensor.refresh()
                    time.sleep_ms(1000)

                    for row in range(8):
                        print()
                        for col in range(8):
                            print('{:4d}'.format(sensor[row, col]), end='')
                    print("\n-------------------------")

                    data = sensor.get_buf()
                    net.send_to_socket(data)
                    # total = 0
                    # for i in range(0, 128, 2):
                    #     total += data[i] | (data[i + 1] << 8)
                    # average = (total / 64) * _PIXEL_TEMP_CONVERSION

                    # print(f"Average temp is {average} C\n")

                    # if average > 22.0:
                    #     led.on()
                    #     net.send_to_socket(bytearray(str(average).encode()))
                    #     time.sleep_ms(200)
                    # else:
                    #     led.off()

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

        led.off()   
>>>>>>> Stashed changes
