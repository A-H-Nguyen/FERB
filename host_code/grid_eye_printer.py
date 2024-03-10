import asyncio

from server_base import FerbProtocol, Server


class GridEyeProtocol(FerbProtocol):
    def handle_data(self, data):
        for i in range(0, len(data), 2):
            pixel_value = data[i] | (data[i + 1] << 8)

            print(pixel_value * 0.25, end='\t')

            if (i + 2) % 16 == 0:
                print()
        print("\n-----------------------------------------\n")


if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(GridEyeProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
