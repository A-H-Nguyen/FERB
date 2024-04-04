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

net = NetHandler()
sensor = AMG88XX(machine.I2C(0, sda=SDA_PIN, scl=SCL_PIN, freq=400000))


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
  
    net.send_to_socket(bytearray("~Calibrating", "utf-8"))
    time.sleep_ms(1000)

    while True:
        try:
            sensor.refresh() # Grid-EYE read data
            time.sleep_ms(100)
            net.send_to_socket(sensor.get_buf())
            time.sleep_ms(100)

        # Change this later -- we want it so that if something fucks up the FERB will try
        # reconnecting to the wi-fi and then the socket server
        except Exception as e:
            print(f"Error: {e}")
            # time.sleep(2)
            break

        except KeyboardInterrupt as k:
            net.disconnect_socket()
            time.sleep_ms(200)
            
            print("Ok, bye")

            led.off()
            
            break

 
if __name__ == "__main__":
    led.on()

    if debug_pin.value() < 1:
        FERB_debug()    
    else:
        FERB_main()

    led.off()
