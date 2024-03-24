import argparse
import asyncio
import datetime


_DEFAULT_IP = '10.42.0.1'
_DEFAULT_PORT = 11111

PIXEL_TEMP_CONVERSION = 0.25

class CLI:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description='Info for socket server')
        self.parser.add_argument('--ip', type=str, 
                                 help='IP Address for Socket Server')
        self.parser.add_argument('--port', type=int, 
                                 help='Port number for Socket Server')
        
        try:
            self.args = self.parser.parse_args()
            if not (self.args.ip and self.args.port):
                raise argparse.ArgumentError(None, "Both IP address and port are required.")
        
        except argparse.ArgumentError as e:
            self.parser.error(str(e))

    def get_ip(self) -> str:
        return self.args.ip
    
    def get_port(self) -> int:
        return self.args.port


class FerbProtocol(asyncio.Protocol):
    def __init__(self):
        self.wait_timer = None
        self.TIME_LIMIT = 10

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        print(f"{datetime.datetime.now()}: Connection from {self.peername}", "\n")

        self.start_wait_timer()  # Start wait timer when connection is made

    def start_wait_timer(self):
        self.wait_timer = asyncio.get_event_loop().call_later(self.TIME_LIMIT, self.timeout)

    def cancel_wait_timer(self):
        if self.wait_timer is not None:
            self.wait_timer.cancel()

    def data_received(self, data):
        print(f"{datetime.datetime.now()}: Data received from {self.peername}")
        
        self.handle_data(data[:128])
        
        self.cancel_wait_timer()  # Cancel current wait timer
        self.start_wait_timer()  # Restart wait timer upon receiving data

    def handle_data(self, data):
        pass

    def connection_lost(self, exc):
        print(f"{datetime.datetime.now()}: Connection with {self.peername} closed", "\n")
        self.cancel_wait_timer()  # Cancel wait timer when connection is lost

    def timeout(self):
        print(f"{datetime.datetime.now()}: Connection timeout - No data received")
        self.transport.close()  # Close connection on timeout


class Server:
    def __init__(self) -> None:
        self.cli = CLI()
    
    async def start_server(self, protocol_class):
        # Get the current event loop
        loop = asyncio.get_running_loop()

        # Create a TCP server using the loop and the protocol class
        server = await loop.create_server(protocol_class, 
                                          self.cli.get_ip(), self.cli.get_port())

        # Get the server address and port
        addr = server.sockets[0].getsockname()
        print(f"Serving on {addr}", "\n")

        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(FerbProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
