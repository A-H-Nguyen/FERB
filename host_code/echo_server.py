import asyncio

from server_base import FerbProtocol, Server


class EchoProtocol(FerbProtocol):
    def handle_data(self, data):
        print(data.decode())


if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.ferb_main(EchoProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
