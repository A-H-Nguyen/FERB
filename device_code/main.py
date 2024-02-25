import machine
import time

from amg88xx import AMG88XX
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

debug_pin = machine.Pin(0, machine.Pin.IN)

if __name__ == "__main__":

    net = NetHandler()
    sensor = AMG88XX(machine.I2C(0, sda=SDA_PIN, scl=SCL_PIN, freq=400000))

    server_conn = False
    
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
            net.send_to_socket(bytearray(b'~ack'))

        while True:
            if debug_mode:
                if not cli.handle_input():
                    break
            else:
                pass
            # _server_ack = net.recv_from_socket()
            # print(str(_server_ack))

            # if _server_ack == b'*err':
            #     break

            # print(debug_pin.value())

            # time.sleep_ms(500)


        #         if not server_conn:
        #             net.connect_to_socket(SERVER_IP, SERVER_PORT)
        #             net.send_to_socket(bytearray(b'~ack'))
        #             _server_ack = net.recv_from_socket()

        #             print(str(_server_ack))

        #             if b'~' in _server_ack:
        #                 print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
        #                 # server_conn = True
        #         break
            # else:
            #     try:
            #         sensor.refresh()
            #         time.sleep_ms(100)
            #         net.send_to_socket(sensor.get_buf())
            #         time.sleep_ms(100)
            #     except Exception as e:
            #         print(f"Error: {e}")
            #         print("Resetting server connection...")
            #         server_conn = False

            #         temp_bytes = device.read_temps()
        #         # device.print_temps(temp_bytes)
        #         device.send_temps(temp_bytes)


            #     server_conn = net.connect_to_socket(SERVER_IP, SERVER_PORT)
            # else:
            #     print(f"Connected to socker server: {SERVER_IP}")


            # break

    except Exception as e:
        print(f"Error: {e}")

    except KeyboardInterrupt as k:
        print("Ok, bye")
