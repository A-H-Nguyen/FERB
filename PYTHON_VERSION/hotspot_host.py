import socket

# Use SOCK_STREAM for TCP    
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
    _HOST = socket.gethostname()
    _IP = socket.gethostbyname(_HOST)
    _PORT = 12345

    print("Host Name =\t", _HOST)
    print("Host IP =\t", _IP)

    _socket.bind((_IP, _PORT))


    print(f"TCP server is listening on {(_IP, _PORT)}")
    _socket.listen(1)
    
    # conn, addr = _socket.accept()
    # with conn:
    #     print(f"Connected by {addr}")
    #     while True:
    #         data = conn.recv(1024)
    #         if not data:
    #             break
    #         conn.sendall(data)
    try:
        while True:
            connection, client_address = _socket.accept()
            print(f"Connection established with {client_address}")

            data = connection.recv(1024)
            print(f"Received data from {client_address}: {data.decode()}")

    #     # Add your own logic to respond to the client if needed
    #     # For example:
    #     # connection.sendall(b"Server received your message")

            connection.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        _socket.close()