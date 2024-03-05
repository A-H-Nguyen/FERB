import argparse
import asyncio

parser = argparse.ArgumentParser(description='Info for socket server')
parser.add_argument('--ip', type=str, help='IP Address for Socket Server', required=True)
parser.add_argument('--port', type=int, help='Port number for Socket Server', required=True)

args = parser.parse_args()


class FerbProtocol(asyncio.Protocol):
    def __init__(self):
        self.wait_timer = None

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        print(f"Connection from {self.peername}")
        self.start_wait_timer()  # Start wait timer when connection is made

    def start_wait_timer(self):
        self.wait_timer = asyncio.get_event_loop().call_later(10, self.timeout)  # Set timeout to 10 seconds

    def cancel_wait_timer(self):
        if self.wait_timer is not None:
            self.wait_timer.cancel()

    def data_received(self, data):
        print(data.decode())
        self.cancel_wait_timer()  # Cancel current wait timer
        self.start_wait_timer()  # Restart wait timer upon receiving data

    def connection_lost(self, exc):
        print(f"Connection with {self.peername} closed")
        self.cancel_wait_timer()  # Cancel wait timer when connection is lost

    def timeout(self):
        print("Timeout: No data received within the specified time")
        self.transport.close()  # Close connection on timeout



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
