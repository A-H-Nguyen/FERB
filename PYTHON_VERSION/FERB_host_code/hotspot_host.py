import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
    _HOST = socket.gethostname()
    _IP = '10.42.0.1'  # taken from ifconfig output
    _PORT = 12345

    print("Host Name =\t", _HOST)
    print("Host IP =\t", _IP)

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

