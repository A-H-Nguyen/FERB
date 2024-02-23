# from FERBCLI import FerbCLI
# from FERBDevice import FerbDevice

import machine
import time

from amg88xx import AMG88XX        # Import the AMG88XX class
from ClientNethandler import NetHandler  # Import the NetHandler class

# Constants for network and server configuration
HOST_SSID = 'JAYVHA'
HOST_PASS = 'test12345'
SERVER_IP = '10.110.85.119'  # IP address of the server, obtained from ifconfig output
SERVER_PORT = 12345      # Arbitrary port number for the server, ensure it's known and available

# Constants for Grid-EYE configuration
SDA_PIN = 16
SCL_PIN = 17
# GRID_EYE_DEFAULT_ADDR = 0x69

HELP_STR = ("\nCommands:\n" + 
            "\th\tPrint this information\n" +
            "\tq\tQuit debugging\n" +
            "\t---\n" +
            "\t1\tPrint Wi-Fi status\n" +
            "\t2\tConnect to Wi-Fi Network\n" +
            "\t3\tDisconnect from Wi-Fi Network\n" +
            "\t4\tConnect to Socket\n" +
            "\t5\tDisconnect from Socket\n" +
            "\t6\tPrint Grid-EYE Reading\n" +
            "\t7\tSend Grid-EYE Reading to host\n")

if __name__ == "__main__":

    net = NetHandler()
    sensor = AMG88XX(machine.I2C(0, sda=SDA_PIN, scl=SCL_PIN, freq=400000))

    print("FERB Debug mode...")
    print(HELP_STR)

    while True:
        user_input = input("cmd # ")

        if user_input == 'q':
            print("Quitting...")
            break

        elif user_input == 'h':
            print(HELP_STR)

        elif user_input == '1':
            if net.is_wifi_connected():
                print(f"Connected to wi-fi on {net.get_ssid()}")
            else:
                print("Not connected to Wi-Fi\n\n" +
                      "Printing Available Networks...")
                net.print_wifi_networks()
        
        elif user_input == '2':
            if net.is_wifi_connected():
                print(f"Already connected to Wi-Fi on {net.get_ssid()}")
            else:
                _ssid = input("SSID: ")
                _passwd = input("Password: ")

                if net.connect_to_wifi(_ssid, _passwd):
                    print(f"Successfully connected to  {_ssid}")
                else:
                    print(f"Could not connect to {_ssid}")
        
        elif user_input == '3':
            if not net.is_wifi_connected():
                print("Connect to a Wi-Fi network first")
            else:
                net.disconnect_wifi()
                print("Disconnected from Wi-Fi network")

        elif user_input == '4':
            _ip = input("Socket server IP: ")
            _port = input("Port number: ")
            if net.connect_to_socket(_ip, int(_port)):
                print(f"Connected to socket server at {_ip}:{_port}")
            else:
                print("Failed to connect to socket server")
        
        elif user_input == '5':
            net.disconnect_socket()
            print("Disconnected from socket server")

        elif user_input == '6':
            print("Printing Grid-EYE Reading...")
            sensor.refresh()
            time.sleep_ms(100)

            data = sensor.get_buf()
            for i in range(0, len(data), 2):
                pixel_value = data[i] | (data[i + 1] << 8)
                print(pixel_value, end=' ')
                if (i + 2) % 16 == 0:
                    print()

        elif user_input == '7':
            print("Sending Grid-EYE Reading to host...")
            sensor.refresh()
            time.sleep_ms(100)
            net.send_to_socket(sensor.get_buf())
            time.sleep_ms(100)
        
        else:
            print("Invalid command. Please enter a valid command from the provided list.")


    # device = FerbDevice(HOST_SSID, HOST_PASS, SERVER_IP, SERVER_PORT,
    #                     GRID_EYE_DEFAULT_ADDR, SDA_PIN, SCL_PIN)
    
    # try:
    # print("Attempt to connect to Wi-FI...")
    # wifi_conn_status = device.connect_to_wifi()
    # if wifi_conn_status != "Success":
    #     raise Exception(f"Could not connect to Wi-Fi network {HOST_SSID}: {wifi_conn_status}")
    # else:
    #     print("Wi-fi success")
    
    # print("Attempt to connect to socket server...")
    # if not device.connect_to_socket():
    #     raise Exception(f"Could not connect to socket at {SERVER_IP}:{SERVER_PORT}")
    # else:
    #     print("Socket success")
    
    # print("Verify Grid-EYE...")
    # if not device.search_for_i2c_device(GRID_EYE_DEFAULT_ADDR):
    #     raise Exception("Grid-EYE sensor not found")
    # else:
    #     print("Grid-EYE success")

    # device.led_high()


    # cli = FerbCLI()


    # debug_mode = False

        # if not debug_mode:
        #     try:
        #         temp_bytes = device.read_temps()
        #         # device.print_temps(temp_bytes)
        #         device.send_temps(temp_bytes)

        #     except Exception as e:
        #         print(f"Error: {e}")

        #     except KeyboardInterrupt as k:
        #         print("Ok")
        #         debug_mode = True
        # else:
        #     try:
        #         print("Debug mode")

        #     # except:
        #     #     print("lol") 
        #     #     debug_mode = False

        #     except KeyboardInterrupt as k:
        #         print("quit debugging")
        #         break