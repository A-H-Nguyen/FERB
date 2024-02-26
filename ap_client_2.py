import socket

from time import sleep

_IP = "127.0.0.1"
_PORT = 8888

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((_IP, _PORT))
    while True:
        try:
            s.sendall(b'~Hi')
            msg = s.recv(1024)
            print(msg)
            
        except KeyboardInterrupt as k:
            print("See ya!")
            break
    s.close()