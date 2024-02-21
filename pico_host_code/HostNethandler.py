import network
import usocket as socket
import time


class NetHandler:
    """
    A class to handle network operations such as connecting to Wi-Fi networks and socket servers.

    Attributes:
        _SSID (str): The SSID of the Wi-Fi network.
        _PASS (str): The password of the Wi-Fi network.
        _IP (str): The IP address of the socket server.
        _PORT (int): The port number of the socket server.
    """

    def __init__(self, _ssid, _pass, _ip, _port) -> None:
        """
        Initializes the network handler with SSID, password, IP address, and port.

        Args:
            _ssid (str): The SSID of the Wi-Fi network.
            _pass (str): The password of the Wi-Fi network.
            _ip (str): The IP address of the socket server.
            _port (int): The port number of the socket server.
        """
        self._SSID = _ssid
        self._PASS = _pass
        self._IP = _ip
        self._PORT = _port

        # Create WLAN object in access point mode
        self.wlan = network.WLAN(network.AP_IF)

        self.wlan.active(True)          # Activate WLAN interface
        self.wlan.config(essid=_ssid, password=_pass)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)  # Create a socket object

    def print_connections(self):
        print("WIP")
        print("---")

    def print_info(self):
        print(self.wlan.ifconfig())
        print("---")
        print(self.wlan.config("hostname"), self.wlan.config("essid"))
        print("---")

    # def print_wifi_networks(self):
    #     """
    #     Scans for available Wi-Fi networks and prints their SSID and RSSI (signal strength).
    #     """
    #     nets = self.wlan.scan()
    #     print(f"\nAvailable networks:")
    #     for net in nets:
    #         print(f"SSID: {net[0]}, RSSI: {net[3]}")
    #     print(f"\n-------------------------------------\n")

    # def connect_to_wifi(self) -> bool:
    #     """
    #     Attempts to connect to the specified Wi-Fi network using SSID and password.

    #     Returns:
    #         bool: True if connection is successful, False otherwise.
    #     """
    #     try:
    #         for i in range(10):
    #             self.wlan.connect(ssid=self._SSID, key=self._PASS)
    #             time.sleep(5)
    #             if self.wlan.isconnected():
    #                 return True

    #     except Exception as e:
    #         print(f"Connection failed: {e}")

    #     return False

    # def connect_to_socket(self) -> bool:
    #     """
    #     Attempts to connect to the specified socket server using IP address and port.

    #     Returns:
    #         bool: True if connection is successful, False otherwise.
    #     """
    #     try:
    #         for i in range(10):
    #             self._socket.connect((self._IP, self._PORT))
    #             print(f"Connected to server at {(self._IP, self._PORT)}")
    #             return True

    #     except Exception as e:
    #         print(f"Connection failed: {e}")

    #     return False

    # def send_to_socket(self, buff: bytearray) -> bool:
    #     """
    #     Sends data to the connected socket server.

    #     Args:
    #         buff (bytearray): The data to be sent, represented as a bytearray.

    #     Returns:
    #         bool: True if data is successfully sent, False otherwise.
    #     """
    #     try:
    #         self._socket.sendall(buff)  # Send data to the socket server

    #     except Exception as e:
    #         print(f"Error in sending data: {e}")
    #         return False

    #     time.sleep_ms(500)  # Delay for 500 milliseconds

    #     return True

    # def recv_from_socket(self) -> bool:
    #     """
    #     Receives data from the connected socket server.

    #     Returns:
    #         bool: True if data is successfully received, False otherwise.
    #     """
    #     try:
    #         self._socket.recv(1024)  # Receive data from the socket server

    #     except Exception as e:
    #         print(f"Error in receiving data: {e}")
    #         return False

    #     time.sleep_ms(500)  # Delay for 500 milliseconds

    #     return True
