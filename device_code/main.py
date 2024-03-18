import machine
import time

from amg88xx import AMG88XX, _PIXEL_TEMP_CONVERSION
from array import array
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

net = NetHandler()
sensor = AMG88XX(machine.I2C(0, sda=SDA_PIN, scl=SCL_PIN, freq=400000))

def calibrate_sensor(sensor, calibration_time=5):

    print("Calibrating sensor for environmental temperature...")

    # total_pixel_values = 64
    # total = 0

    hot_pixel = 0 # Value of hottest pixel
    

    start_time = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start_time) < calibration_time * 1000:
        sensor.refresh()
        time.sleep_ms(900)  # Adjust the sleep time if needed
        pixels = array('H', sensor.get_buf())

        # print(pixels)

        local_max = 0
        for p in pixels:
            if p > local_max:
                local_max = p

        # print("Hottest pixel is", local_max)

        if local_max > hot_pixel:
            hot_pixel = local_max

        # print("\n-------------------------")

        # print_grid_eye(sensor)

    #     for i in range(0, 128, 2):
    #         total += pixels[i] | (pixels[i + 1] << 8)

    # average = int((total / (total_pixel_values * calibration_time)) * _PIXEL_TEMP_CONVERSION)

    # print(f"Enviromental temperature is {average} C")
    # print("Calibration Complete\n")

    # average = 0
    # return average
    return hot_pixel


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
    # data_array = np.frombuffer(data, dtype=np.uint16)


def FERB_debug():
    print("FERB booting in Debug mode...\n")
    cli = FerbCLI(sensor=sensor, nethandler=net)
    while True:
        if not cli.handle_input():
            break    





def FERB_main():
    if not net.is_wifi_connected():
        print(f"Attempting to connect to {HOST_SSID} ...")
        # if not net.connect_to_wifi(10, HOST_SSID, HOST_PASS):
        #     raise Exception(f"Could not connect to wi-fi on {HOST_SSID}")
        net.connect_to_wifi(5, HOST_SSID, HOST_PASS)
    print(f"Successfully connected to {net.get_ssid()}\n")
    print(f"Attempting to connect to socket {SERVER_IP}:{SERVER_PORT} ...")
    
    net.connect_to_socket(SERVER_IP, SERVER_PORT)
    
    print(f"Socket connection successful\n")

    enviro = calibrate_sensor(sensor)
    net.send_to_socket(bytearray("~" + str(enviro * _PIXEL_TEMP_CONVERSION), "utf-8"))
    time.sleep_ms(1000)

    while True:
        try:
            # enviro = calibrate_sensor(sensor, 1)
            # net.send_to_socket(bytearray("~" + str(enviro * _PIXEL_TEMP_CONVERSION), "utf-8"))

            # net.send_to_socket(bytearray("~" + str(21), "utf-8"))

            # time.sleep_ms(1000)

            sensor.refresh() # Grid-EYE read data
            time.sleep_ms(100)
            # print_grid_eye(sensor)
            net.send_to_socket(sensor.get_buf())
            # time.sleep_ms(100)

            # # net.send_to_socket(bytearray(b'hey'))
            # time.sleep_ms(1000)

        # Change this later -- we want it so that if something fucks up the FERB will try
        # reconnecting to the wi-fi and then the socket server
        except Exception as e:
            print(f"Error: {e}")
            # time.sleep(2)
            break

        except KeyboardInterrupt as k:
            net.disconnect_socket()
            time.sleep_ms(200)
            
            # net.disconnect_wifi()
            # time.sleep_ms(200)

            print("Ok, bye")

            led.off()
            
            break

 

if __name__ == "__main__":
    led.on()

    if debug_pin.value() < 1:
        FERB_debug()    
    else:
        FERB_main()
