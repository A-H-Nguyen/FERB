import asyncio

from server_base import CLI, FerbProtocol, ferb_main


class echo_server(FerbProtocol):
    def handle_data(self, data):
        print(data.decode())


if __name__ == "__main__":
    cli = CLI()

    try:
        asyncio.run(ferb_main(echo_server, cli.get_ip(), cli.get_port()))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
