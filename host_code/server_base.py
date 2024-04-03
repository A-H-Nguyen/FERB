import argparse
import asyncio
import datetime
import threading


_DEFAULT_IP = '10.42.0.1'
_DEFAULT_PORT = 11111

PIXEL_TEMP_CONVERSION = 0.25


class FerbProtocol(asyncio.Protocol):
    def __init__(self):
        self.wait_timer = None
        self.TIME_LIMIT = 10

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        self.print_timestamp(f"Connection from {self.peername}")

        self.start_wait_timer()  # Start wait timer when connection is made

    def start_wait_timer(self):
        self.wait_timer = asyncio.get_event_loop().call_later(self.TIME_LIMIT, self.timeout)

    def cancel_wait_timer(self):
        if self.wait_timer is not None:
            self.wait_timer.cancel()

    def data_received(self, data):
        self.print_timestamp(f"Data received from {self.peername}")
        
        self.handle_data(data[:128])
        
        self.cancel_wait_timer()  # Cancel current wait timer
        self.start_wait_timer()  # Restart wait timer upon receiving data

    def handle_data(self, data):
        pass

    def connection_lost(self, exc):
        self.print_timestamp(f"Connection with {self.peername} closed")
        self.cancel_wait_timer()  # Cancel wait timer when connection is lost

    def timeout(self):
        self.print_timestamp("Connection timeout - No data received")
        self.transport.close()  # Close connection on timeout

    def print_timestamp(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"{timestamp}\n{message}\n")


class CLI:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description='Info for socket server')
        self.parser.add_argument('--ip', type=str, 
                                 help='IP Address for Socket Server')
        self.parser.add_argument('--port', type=int, 
                                 help='Port number for Socket Server')
        self.args = self.parser.parse_args()

    def get_ip(self) -> str:
        if self.args.ip:
            return self.args.ip
        else:
            return _DEFAULT_IP
    
    def get_port(self) -> int:
        if self.args.port:
            return self.args.port
        else:
            return _DEFAULT_PORT


class Server:
    def __init__(self, protocol_class) -> None:
        self.protocol = protocol_class
        self.cli = CLI()
    
    async def start_server(self):
        # Get the current event loop
        loop = asyncio.get_running_loop()

        # Create a TCP server using the loop and the protocol class
        server = await loop.create_server(self.protocol,
                                          self.cli.get_ip(), self.cli.get_port())
        print(f"Serving on {server.sockets[0].getsockname()}", "\n")
        
        async with server:
            await server.serve_forever()

    def run(self):
        asyncio.run(self.start_server())


if __name__ == "__main__":
    try:
        server = Server(protocol_class=FerbProtocol)
        threading.Thread(target=server.run).start()
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
