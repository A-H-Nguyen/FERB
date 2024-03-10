import time

from amg88xx import AMG88XX
from ClientNethandler import NetHandler

class FerbCLI:
    """
    A class that implements a user interactive debugging interface on a FERB device 
    """

    def __init__(self, sensor: AMG88XX, nethandler: NetHandler) -> None:
        """
        Initializes the FerbCLI class with a sensor and network handler.

        Args:
            sensor (AMG88XX): The sensor object.
            nethandler (NetHandler): The network handler object.
        """
        self.sensor = sensor
        self.nethandler = nethandler
        self.HELP_STR = ("\nCommands:\n" + 
                         "\th\tPrint this information\n" +
                         "\tq\tQuit debugging\n" +
                         "\t---\n" +
                         "\t1\tPrint Wi-Fi status\n" +
                         "\t2\tConnect to Wi-Fi Network\n" +
                         "\t3\tDisconnect from Wi-Fi Network\n" +
                         "\t4\tConnect to Socket\n" +
                         "\t5\tDisconnect from Socket\n" +
                         "\t6\tSend Message to Server\n" +
                         "\t7\tPrint Grid-EYE Reading\n" +
                         "\t8\tSend Grid-EYE Reading to host\n")
        print(self.HELP_STR)

    def handle_input(self) -> bool:
        """
        Handles user input commands.

        Returns:
            bool: True if the program should continue, False if it should quit.
        """
        user_input = input("cmd ~ ")

        if user_input == 'q':
            print("Quitting...")
            return False

        elif user_input == 'h':
            print(self.HELP_STR)

        elif user_input == '1':
            if self.nethandler.is_wifi_connected():
                print(f"Connected to wi-fi on {self.nethandler.get_ssid()}")
            else:
                print("Not connected to Wi-Fi\n\n" +
                      "Printing Available Networks...")
                self.nethandler.print_wifi_networks()
        
        elif user_input == '2':
            if self.nethandler.is_wifi_connected():
                print(f"Already connected to Wi-Fi on {self.nethandler.get_ssid()}")
            else:
                _ssid = input("SSID: ")
                _passwd = input("Password: ")

                if self.nethandler.connect_to_wifi(max_attempts=5,
                                                   ssid=_ssid, password=_passwd):
                    print(f"Successfully connected to  {_ssid}")
                else:
                    print(f"Could not connect to {_ssid}")
        
        elif user_input == '3':
            if not self.nethandler.is_wifi_connected():
                print("Connect to a Wi-Fi network first")
            else:
                self.nethandler.disconnect_wifi()
                print("Disconnected from Wi-Fi network")

        elif user_input == '4':
            _ip = input("Socket server IP: ")
            _port = input("Port number: ")
            self.nethandler.connect_to_socket(_ip, int(_port))
            print(f"Connected to socket server at {_ip}:{_port}")
            
        elif user_input == '5':
            self.nethandler.send_to_socket(bytearray(b'~close'))
            self.nethandler.disconnect_socket()
            print("Disconnected from socket server")

        elif user_input == '6':
            _msg = input("Message for server: ")
            _b = bytearray()
            _b.extend(_msg.encode())
            self.nethandler.send_to_socket(_b)

        elif user_input == '7':
            print("Printing Grid-EYE Reading...")
            self.sensor.refresh()
            time.sleep_ms(100)

            for row in range(8):
                print()
                for col in range(8):
                    print('{:4d}'.format(self.sensor[row, col]), end='')
            print("\n-------------------------")

        elif user_input == '8':
            print("Sending Grid-EYE Reading to host...")
            self.sensor.refresh()
            time.sleep_ms(100)
            self.nethandler.send_to_socket(self.sensor.get_buf())
            time.sleep_ms(100)
        
        else:
            print("Invalid command.")
        
        return True
