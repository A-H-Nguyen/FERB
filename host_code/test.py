import asyncio
import pygame
import numpy as np

from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION
from scipy.interpolate import RegularGridInterpolator


# Constants for Pygame visualization
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400
PIXEL_SIZE = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Number of pixels for both original Grid-EYE output, and interpolated output
_GRID_LEN = 8
_INTRP_LEN = 16
_GRAYSCALE = 255


class GridEyeProtocol(FerbProtocol):
    def __init__(self):
        super().__init__()
        
        # Generate x and y coordinates for the original and interpolated Grid-EYE output
        self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
        self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
        self.interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)

        # Used for background subtraction
        self.background = np.zeros(shape=(_INTRP_LEN, _INTRP_LEN))
        
        # Variables for calibration sequence
        self.cal_finished = True
        self.cal_counter = 1

        # Default values for range of temps post-background subtraction
        self.min_val = 0
        self.max_val = 5

    def calibrate(self, input_matrix) -> None:
        self.background += input_matrix
        self.cal_counter += 1

        if self.cal_counter > 5:
            self.background = self.background / 5 # Hardcode this value instead
                                                  # I was using the counter for some fucking reason
            self.cal_finished = True
            print("\nCalibrating done.")
            print("\n-----------------------------------------\n")

    def convert_to_grayscale(self, value) -> int:
        return int(((value - self.min_val) / (self.max_val - self.min_val)) * _GRAYSCALE)

    def normalize_data(self, data):
        for row in range(_INTRP_LEN):
            for col in range(_INTRP_LEN):
                if data[row,col] < self.min_val:
                    self.min_val = data[row,col]
                if data[row,col] > self.max_val:
                    self.max_val = data[row,col]

        print("Min val:", self.min_val,
              "Max val:", self.max_val)

        for row in range(_INTRP_LEN):
            for col in range(_INTRP_LEN):
                data[row,col] = self.convert_to_grayscale(data[row,col])

        print(data)

    def handle_data(self, data):
        msg = data.decode()
        if msg[0] == '~':
            # start calibration sequence here
            print("\nCalibrating sensor. Get the fuck out of the way\n")
            self.cal_finished = False
            return

        # Convert the bytearray to a numpy array of 16-bit integers (short ints)
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

        if data_array.size != 64:
            print("Bad packet")
            return

        # Convert the bytearray to a numpy array of 16-bit integers (short ints)
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

        # Reshape the array to form an 8x8 matrix
        matrix = data_array.reshape((8, 8))

        # Create a scipy interpolation function for our temperature reading
        interp_func = RegularGridInterpolator((self.orig_coords, self.orig_coords), matrix)
        interp_matrix = interp_func((self.interp_Y, self.interp_X))
        
        if not self.cal_finished:
            self.calibrate(interp_matrix)
            return
        
        diff_matrix = np.round(interp_matrix - self.background) 
        # print(diff_matrix)
        self.normalize_data(diff_matrix)
        # for row in range(_INTRP_LEN):
        #     for col in range(_INTRP_LEN):
        #         print(diff_matrix[row,col], end='  ')
        #     print('\n')
        # print(interp_matrix)
        # print(diff_matrix)
        print("\n-----------------------------------------\n")


if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(GridEyeProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
