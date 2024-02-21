import time
# import socket

from HostNethandler import NetHandler

class Ferb:
    def __init__(self, _ssid, _pass,  _ip, _port) -> None:
        self._SSID = _ssid
        self._PASS = _pass
        self._NET = NetHandler(_ssid, _pass,  _ip, _port)

    def print_status(self) -> None:
        self._NET.print_info()
        self._NET.print_connections()



