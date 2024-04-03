import asyncio
import random
import threading
import numpy as np
import tkinter as tk

from scipy.interpolate import RegularGridInterpolator
from server_base import FerbProtocol, PIXEL_TEMP_CONVERSION
from time import sleep

# Number of pixels for both original Grid-EYE output, and interpolated output
_GRID_LEN = 8
_INTRP_LEN = 16
_GRAYSCALE = 255


class ThermalCam:
    def __init__(self, canvas: tk.Canvas, len):
        self._canvas = canvas
        self._resolution = len
        self._draw_len = len / _INTRP_LEN

    def draw_thermal_image(self, temps):
        for row in range(_INTRP_LEN):
            for col in range(_INTRP_LEN):
                # color = "#%02x%02x%02x" % (temps[row,col], 
                #                            temps[row,col], 
                #                            temps[row,col])

                if temps[row,col] > 100:
                    color = "black"
                else:
                    color = "white"

                x0 = col * self._draw_len
                y0 = row * self._draw_len
                x1 =  x0 + self._draw_len
                y1 =  y0 + self._draw_len

                self._canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='')

    # def start(self):
    #     self.thread = threading.Thread(target=self.draw_thermal_image)
    #     self.thread.start()

    # def stop(self):
    #     if self.thread:
    #         self.thread.join()


class GridEyeProtocol(FerbProtocol):
    def __init__(self, canvas: tk.Canvas, screen_len):
        super().__init__()

        self.cam = ThermalCam(canvas, screen_len)
        
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
            self.background /= 5 # Hardcode this value instead
                                 # I was using the counter for some fucking reason
            self.cal_finished = True
            self.print_timestamp("Calibration finished.")

    # def convert_to_grayscale(self, value) -> int:
    #     return int(((value - self.min_val) / (self.max_val - self.min_val)) * _GRAYSCALE)

    def normalize_data(self, data):
        for row in range(_INTRP_LEN):
            for col in range(_INTRP_LEN):
                data[row,col] = int(((data[row,col] - self.min_val) / 
                                     (self.max_val - self.min_val)) * _GRAYSCALE)

    def handle_data(self, data):
        try:
            msg = data.decode()
            if msg[0] == '~':
                # start calibration sequence here
                self.print_timestamp("Calibrating sensor. Get the fuck out of the way")
                self.cal_finished = False
                return

            # Convert the bytearray to a numpy array of 16-bit integers (short ints)
            data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

            if data_array.size != 64:
                self.print_timestamp("Bad packet")
                return

            # Convert the bytearray to a numpy array of 16-bit integers (short ints)
            data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION
            interp_func = RegularGridInterpolator((self.orig_coords, 
                                                   self.orig_coords), 
                                                   data_array.reshape((8,8)))
            temperatures = interp_func((self.interp_Y, self.interp_X))
            
            if not self.cal_finished:
                self.calibrate(temperatures)
                return
            
            diff_matrix = np.clip(np.round(temperatures - self.background),
                                  self.min_val, self.max_val)
            self.normalize_data(diff_matrix)
            
            self.cam.draw_thermal_image(diff_matrix)

            # # Update heatmap visualization
            # self.update_heatmap(diff_matrix)
            # print(diff_matrix)

            # print("\n-----------------------------------------\n")
        
        except Exception as e:
            print(f"error: {e}")

    # def update_heatmap(self, data):
    #     for x in range(_INTRP_LEN):
    #         for y in range(_INTRP_LEN):
    #             rgb_color = "#%02x%02x%02x" % (data[x,y], data[x,y], data[x,y])
    #             # Check if the pixel has changed
    #             # if not self.data_history or matrix[x, y] != self.data_history[-1][x, y]:
    #             # if intensity_matrix[x, y]:
    #             #     # Determine the rectangle's position and size
    #             #     rect_position = (x * PIXEL_SIZE, y * PIXEL_SIZE)
    #             #     rect_size = (PIXEL_SIZE, PIXEL_SIZE)
    #             #     # Draw a rectangle for the pixel if it has changed
    #             #     pygame.draw.rect(self.window, 
    #             #                      (intensity_matrix[x, y], 
    #             #                       intensity_matrix[x, y], 
    #             #                       intensity_matrix[x, y]), 
    #             #                       (rect_position, rect_size))
    #             #     # pygame.draw.rect(self.window, 
    #             #     #                  (matrix[x, y], matrix[x, y], matrix[x, y]), 
    #             #     #                  (rect_position, rect_size))



"""
Old Thermal Cam below. The old code created a server, and used graphics.py to render
the thermal cam
"""
# import asyncio
# import numpy as np

# from graphics import *
# from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION

# # Number of pixels for both original Grid-EYE output, and interpolated output
# _GRID_LEN = 8
# _INTRP_LEN = 16

# class ThermalCam:
#     def __init__(self, resolution=400, min_temp=15, max_temp=30, 
#                  low_color=(77, 255, 195), high_color=(255, 0, 0)) -> None:
#         # Define the size of the thermal image grid
#         self._RESOLUTION = resolution

#         # Initialize temperature parameters
#         self._MIN_TEMP = min_temp  # Minimum temperature value
#         self._MAX_TEMP = max_temp  # Maximum temperature value
#         self._temp_diff = self._MAX_TEMP - self._MIN_TEMP

#         # Set color values
#         self._LOW_COLOR = low_color
#         self._HIGH_COLOR = high_color

#         # Compute color interpolation differences
#         self._red = self._HIGH_COLOR[0] - self._LOW_COLOR[0]
#         self._green = self._HIGH_COLOR[1] - self._LOW_COLOR[1]
#         self._blue = self._HIGH_COLOR[2] - self._LOW_COLOR[2]

#         # Precompute the length of grid-eye pixels for drawing
#         self._draw_distance = self._RESOLUTION / _GRID_LEN

#         # Set the window with the given resolution
#         self.win = GraphWin("Thermal Image", self._RESOLUTION, self._RESOLUTION)

#     def map_temperature(self, val):
#         # Normalize val between 0 and 1
#         normalized_val = (val - self._MIN_TEMP) / self._temp_diff

#         # Interpolate RGB values
#         r = int(self._LOW_COLOR[0] + normalized_val * self._red)
#         g = int(self._LOW_COLOR[1] + normalized_val * self._green)
#         b = int(self._LOW_COLOR[2] + normalized_val * self._blue)

#         # Ensure that the color values are between 0 and 255
#         return color_rgb(np.clip(r, 0, 255),
#                          np.clip(g, 0, 255),
#                          np.clip(b, 0, 255))

#     def draw_thermal_image(self, temps):
#         for row in range(_GRID_LEN):
#             for col in range(_GRID_LEN):
#                 color = self.map_temperature(temps[row, col])
#                 rect = Rectangle(Point(col * self._draw_distance, row * self._draw_distance), 
#                                  Point((col + 1) * self._draw_distance, (row + 1) * self._draw_distance))
#                 rect.setFill(color)
#                 rect.draw(self.win)


# class ThermalCamProtocol(FerbProtocol):
#     def __init__(self):
#         self.wait_timer = None
#         self.TIME_LIMIT = 10

#         self.cam = ThermalCam()

#     def data_received(self, data): # redefine this to overwrite date-time printing
#         self.handle_data(data[:128])
        
#         self.cancel_wait_timer()  # Cancel current wait timer
#         self.start_wait_timer()  # Restart wait timer upon receiving data

#     def handle_data(self, data):
#         temps_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION
        
#         # Check the size of our received data. This is neccessary if we run the Pico very fast,
#         # as in having a sleep of < 100 ms every time we send data.
#         # If we run the Pico very fat, then sometimes either the full 128 bytes will not be sent,
#         # or multiple packets can be received at once, making temps_array too large.
#         # Furthermore, for the current unoptimized drawing algorithm, a sleep of < 250 ms doesn't
#         # show a noticable performance increase.
#         if temps_array.size != 64:
#             print("skipped")
#             return
        
#         temps_matrix = temps_array.reshape((_GRID_LEN, _GRID_LEN))

#         self.cam.draw_thermal_image(temps_matrix)

#     def connection_lost(self, exc):
#         print(f"Connection with {self.peername} closed")
#         self.cam.win.close()
#         self.cancel_wait_timer()  # Cancel wait timer when connection is lost


# if __name__ == "__main__":
#     try:
#         server = Server()
#         asyncio.run(server.start_server(ThermalCamProtocol))
        
#     except KeyboardInterrupt as k:
#         print("\nGoodbye cruel world\n")
