import network
import usocket as socket
import uselect as select
import time

class network_handler:
    def __init__(self, _ssid, _pass, _ip, _port, station_mode:bool=True) -> None:
        self._SSID = _ssid
        self._PASS = _pass
        self._IP = _ip
        self._PORT = _port

        if station_mode:
            self.wlan = network.WLAN(network.STA_IF)
        else:
            self.wlan = network.WLAN(network.AP_IF)
        self.wlan.active(True)

        self._socket = socket.socket()

    def _get_networks(self):
        nets = self.wlan.scan()
        print(f"\nAvailable networks:")
        for net in nets:
            # Access the 0th element of the tuple for SSID
            # Access the 3rd element of the tuple for RSSI
            print(f"SSID: {net[0]}, RSSI: {net[3]}")
        print(f"\n-------------------------------------\n")

    def _connect_wifi(self):    
        _wlan_connected = False
        while not _wlan_connected:
            print(f"Attempting to connect to {self._SSID}...\n")
            self.wlan.connect(ssid=self._SSID, key=self._PASS)
            time.sleep(5)

            if self.wlan.isconnected():
                _wlan_connected = True

        print(f"Connected to network on {self._SSID}")

    def _connect_socket(self):
        _socket_connected = False
        while not _socket_connected:
            try:
                self._socket.connect((self._IP, self._PORT))
                _socket_connected = True
                print(f"Connected to server at {(self._IP, self._PORT)}")

            except Exception as e:
                print(f"Connection failed: {e}")
                time.sleep(3)

        # Virtual Handshake to verify that server has been connected to:
        self._socket.sendall(b"Hello From FERB Unit")
        time.sleep_ms(500)

        data = self._socket.recv(1024)
        time.sleep_ms(500)

        if data != b'ACK':
            raise Exception(f"Host on {self._IP} sent invalid ACK: {data}")
        else:
            print("Acknowledgement from host server recieved!")


