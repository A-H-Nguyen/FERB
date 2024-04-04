import numpy as np

from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION


class GridEyeProtocol(FerbProtocol):
    def handle_data(self, data):
        if len(data) != 128:
            return

        # Convert the bytearray to a numpy array of 16-bit integers (short ints)
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

        # Reshape the array to form an 8x8 matrix
        matrix = data_array.reshape((8, 8))

        print(matrix)
        print("\n-----------------------------------------\n")


if __name__ == "__main__":
    try:
        server = Server(protocol_class=GridEyeProtocol)
        server.run()
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
