import argparse
import asyncio

parser = argparse.ArgumentParser(description='Info for socket server')
parser.add_argument('--ip', type=str, help='IP Address for Socket Server', required=True)
parser.add_argument('--port', type=int, help='Port number for Socket Server', required=True)

args = parser.parse_args()


class FerbProtocol(asyncio.Protocol):
    # This method is called when a new client connection is established
    def connection_made(self, transport):
        # Save a reference to the transport object
        self.transport = transport
        # Get the peer name of the client
        self.peername = transport.get_extra_info("peername")
        # Print a message
        print(f"Connection from {self.peername}")

    # This method is called when data is received from the client
    def data_received(self, data):
        # Decode the data from bytes to string
        msg = data.decode()
        # print(f"Data received from {self.peername}:\tFlag={msg[0]}")
        
        # # Check data flag (first byte of message)
        # # If first byte is '~' then the FERB is in debug mode and is awaiting a command
        if msg[0] == '~':
        #     self.debug_cmd()
            pass
  
        # # If first byte is '>' then FERB is in debug mode and is sending cmd output
        elif msg[0] == '>':
        #     print(f"{msg}")
            pass

        # Otherwise, FERB is in normal mode and is sending Grid-EYE data
        else:
            print("Grid-EYE reading received:")
            self.parse_grid_eye(data)
    
    # This method is called when the client connection is closed
    def connection_lost(self, exc):
        print(f"Connection with {self.peername} closed")
        # Close the transport
        self.transport.close()

    # Handle sending debug commands to the FERB in debug mode. 
    # NOTE: Currently, the server can only manage debugging one FERB at a time
    def debug_cmd(self):
        cmd = input("CMD ~ ")
        self.transport.write(cmd.encode())

        if cmd == 'q' or cmd == 'quit':
            self.transport.close()

    # def parse_grid_eye(self, data):
    #     temps = []
    #     for i in range(0, len(data), 2):
    #         pixel_value = data[i] | (data[i+1] << 8)
    #         temps.append(pixel_value)

    #         print(pixel_value, end=' ')

    #         if (i + 2) % 16 == 0:
    #             print()

    #         if len(temps) > 63:
    #             print()
    #             break


async def main(protocol_class):
    # Get the current event loop
    loop = asyncio.get_running_loop()

    # Create a TCP server using the loop and the protocol class
    server = await loop.create_server(protocol_class, args.ip, args.port)

    # Get the server address and port
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main(FerbProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
