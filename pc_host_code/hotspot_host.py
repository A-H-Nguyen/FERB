import argparse
import socket
# import threading
import asyncio

parser = argparse.ArgumentParser(description='Info for socket server')
parser.add_argument('--ip', type=str, help='IP Address for Socket Server', required=True)
parser.add_argument('--port', type=int, help='Port number for Socket Server', required=True)

args = parser.parse_args()

_IP = args.ip
_PORT = args.port


class FerbProtocol(asyncio.Protocol):
    # This method is called when a new client connection is established
    def connection_made(self, transport):
        # Save a reference to the transport object
        self.transport = transport
        # Get the peer name of the client
        peername = transport.get_extra_info("peername")
        # Print a message
        print(f"Connection from {peername}")

    # This method is called when data is received from the client
    def data_received(self, data):
        # Decode the data from bytes to string
        message = data.decode()
        # Print a message
        print(f"Data received: {message}")
        # Send back the same data to the client
        # self.transport.write(data)
        # # Print a message
        # print(f"Data sent: {message}")

    # This method is called when the client connection is closed
    def connection_lost(self, exc):
        # Print a message
        print("Connection closed")
        # Close the transport
        self.transport.close()


# async def FerbProtocol(reader, writer):
#     data = await reader.read(100)
#     message = data.decode()
#     addr = writer.get_extra_info('peername')

#     print(f'Received {message} from {addr}')

#     print(f'Send: {message}')
#     writer.write(data)
#     await writer.drain()

#     if message == '~close':
#         writer.close()


async def main():
    # Get the current event loop
    loop = asyncio.get_running_loop()

    # Create a TCP server using the loop and the protocol class
    server = await loop.start_server(FerbProtocol, _IP, _PORT)

    # Get the server address and port
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())


# def handle_client(c):
#     message = c.recv(1024)
#     print('Received:', message)
#     c.send(b'Echo:' + message)
#     c.close()


# if __name__ == "__main__":

#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

#         s.bind((_IP, _PORT))

#         print(f"TCP server is listening on {(_IP, _PORT)}...\n")

#         s.listen(1)
#         connection, client_address = s.accept()
#         print(f"Connection established with {client_address}")

#         threading.Thread(target=handle_client, args=(connection,)).start()

    #     while True:
    #         try:
    #             pass
    #             # s.sendall(b'~hello from server')
    #             # data = connection.recv(1024)
    #             # if not data:
    #             #     raise Exception("Connection closed by client.")
                
    #             # if data == bytearray(b'~ack'):
    #             #     print(str(data))


    #             # temps = []
    #             # for i in range(0, len(data), 2):
    #             #     pixel_value = data[i] | (data[i+1] << 8)
    #             #     temps.append(pixel_value)

    #             #     print(pixel_value, end=' ')

    #             #     if (i + 2) % 16 == 0:
    #             #         print()

    #             #     if len(temps) > 63:
    #             #         print()
    #             #         break

    #         except Exception as e:
    #             print(f"Error: {e}")
    #             break

    #         except KeyboardInterrupt as k:
    #             print("Server terminated by keyboard interrupt.")
    #             connection.close()
    #             break

    #     s.close()

