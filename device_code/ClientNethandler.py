import network
import usocket as socket
import time


class NetHandler:
    """
    A class to handle network operations such as connecting to Wi-Fi networks and socket servers.
    """

    def __init__(self) -> None:
        """
        Initializes the network handler.
        """
        self.wlan = network.WLAN(network.STA_IF)  # Create WLAN object in station mode
        self.wlan.active(True)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket

    def print_wifi_networks(self) -> None:
        """
        Scans for available Wi-Fi networks and prints their SSID and RSSI (signal strength).
        """
        nets = self.wlan.scan()
        print(f"\nAvailable networks:")
        for net in nets:
            print(f"SSID: {net[0]}, RSSI: {net[3]}")
        print(f"\n-------------------------------------\n")

    def is_wifi_connected(self):
        """
        Checks if the device is connected to a Wi-Fi network.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.wlan.isconnected()

    def get_ssid(self):
        """
        Gets the SSID of the currently connected Wi-Fi network.

        Returns:
            str: The SSID.
        """
        return self.wlan.config('ssid')

    def connect_to_wifi(self, ssid, password) -> bool:
        """
        Attempts to connect to the specified Wi-Fi network using SSID and password.

        Args:
            ssid (str): The SSID of the Wi-Fi network.
            password (str): The password of the Wi-Fi network.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            self.wlan.connect(ssid=ssid, key=password)
            time.sleep(10)

            if self.wlan.isconnected():
                return True

        except Exception as e:
            print(f"Connection failed: {e}")

        return False

    def disconnect_wifi(self):
        """
        Disconnects from the current Wi-Fi network.
        """
        self.wlan.disconnect()

    def connect_to_socket(self, ip, port):
        """
        Attempts to connect to the specified socket server using IP address and port.

        Args:
            ip (str): The IP address of the socket server.
            port (int): The port number of the socket server.
        """
        try:
            self._socket.connect((ip, port))
            time.sleep_ms(250)

        except Exception as e:
            print(f"Error in Connection Attempt: {e}")

    def disconnect_socket(self):
        """
        Closes the socket connection.
        """
        self._socket.close()

    def send_to_socket(self, buff: bytearray):
        """
        Sends data to the connected socket server.

        Args:
            buff (bytearray): The data to be sent, represented as a bytearray.
        """
        try:
            self._socket.sendall(buff) # Send data to the socket server

        except Exception as e:
            print(f"Error in sending data: {e}")

        time.sleep_ms(250)

    def recv_from_socket(self) -> bytes:
        """
        Receives data from the connected socket server.

        Returns:
            bytes: The received data.
        """
        try:
            data = self._socket.recv(1024) # Receive data from the socket server

        except Exception as e:
            print(f"Error in receiving data: {e}")
            return b'*err'

        time.sleep_ms(250)

        return data
