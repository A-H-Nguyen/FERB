import argparse
import socket

parser = argparse.ArgumentParser(description='Info for socket server')
parser.add_argument('--ip', type=str, help='IP Address for Socket Server', required=True)
parser.add_argument('--port', type=int, help='Port number for Socket Server', required=True)

args = parser.parse_args()

_IP = args.ip
_PORT = args.port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:

    _socket.bind((_IP, _PORT))

    print(f"TCP server is listening on {(_IP, _PORT)}...\n")

    _socket.listen(1)
    connection, client_address = _socket.accept()
    print(f"Connection established with {client_address}")

    while True:
        try:
            temps = []

            data = connection.recv(1024)
            if not data:
                raise Exception("Connection closed by client.")
            
            for i in range(0, len(data), 2):
                pixel_value = data[i] | (data[i+1] << 8)
                temps.append(pixel_value)

                print(pixel_value, end=' ')

                if (i + 2) % 16 == 0:
                    print()

                if len(temps) > 63:
                    print()
                    break

        except Exception as e:
            print(f"Error: {e}")

        except KeyboardInterrupt as k:
            print("Server terminated by keyboard interrupt.")
            connection.close()
            break

    _socket.close()

