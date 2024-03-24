import asyncio
import numpy as np

from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION


class GridEyeProtocol(FerbProtocol):
    def __init__(self):
        self.wait_timer = None
        self.TIME_LIMIT = 10

        self.temp_normalize_val: float = 0.00 # Temperature normalization value

    def handle_data(self, data):
        msg = data.decode()

        if msg[0] == "~":
            self.temp_normalize_val = float(msg[1:-1])
            print("Hot Pixel:", self.temp_normalize_val, "Degrees C", "\n")
            return
        
        # Convert the bytearray to a numpy array of 16-bit integers (short ints)
        temps_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION
        temps_normalized = np.round(temps_array - self.temp_normalize_val).astype(int)
        
        matrix = np.clip(temps_normalized, 0, None).reshape((8, 8))

        print(matrix, "\n-----------------------------------------\n")


if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(GridEyeProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
