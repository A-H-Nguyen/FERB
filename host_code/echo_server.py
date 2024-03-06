import argparse
import asyncio

from server_base import CLI, FerbProtocol, ferb_main

parser = argparse.ArgumentParser(description='Info for socket server')
parser.add_argument('--ip', type=str, help='IP Address for Socket Server', required=True)
parser.add_argument('--port', type=int, help='Port number for Socket Server', required=True)

args = parser.parse_args()


class echo_server(FerbProtocol):
    def handle_data(self, data):
        print(data.decode())


if __name__ == "__main__":
    cli = CLI()

    try:
        asyncio.run(ferb_main(echo_server, cli.get_ip(), cli.get_port()))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
