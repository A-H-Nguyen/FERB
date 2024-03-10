import asyncio

from server_base import FerbProtocol, Server


class EchoProtocol(FerbProtocol):
    def start_wait_timer():
        pass

    def handle_data(self, data):
        print(data.decode())


if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(EchoProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
