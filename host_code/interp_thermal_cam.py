import asyncio
import numpy as np

from graphics import *
from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION
from scipy.interpolate import RegularGridInterpolator

# Number of pixels for both original Grid-EYE output, and interpolated output
_GRID_LEN = 8
_INTRP_LEN = 16

class ThermalCam:
    def __init__(self, resolution=400, min_temp=15, max_temp=30, 
                 low_color=(77, 255, 195), high_color=(255, 0, 0)) -> None:
        # Define the size of the thermal image grid
        self._RESOLUTION = resolution

        # Set the window with the given resolution
        self.win = GraphWin("Thermal Image", self._RESOLUTION, self._RESOLUTION)

        # Initialize temperature parameters
        self._MIN_TEMP = min_temp  # Minimum temperature value
        self._MAX_TEMP = max_temp  # Maximum temperature value
        self._temp_diff = self._MAX_TEMP - self._MIN_TEMP

        # Set color values
        self._LOW_COLOR = low_color
        self._HIGH_COLOR = high_color

        # Compute color interpolation differences
        self._red = self._HIGH_COLOR[0] - self._LOW_COLOR[0]
        self._green = self._HIGH_COLOR[1] - self._LOW_COLOR[1]
        self._blue = self._HIGH_COLOR[2] - self._LOW_COLOR[2]

        # Precompute the length of grid-eye pixels for drawing
        # self._draw_distance = self._RESOLUTION / _GRID_LEN
        self._draw_distance = self._RESOLUTION / _INTRP_LEN

    def map_temperature(self, val):
        # Normalize val between 0 and 1
        normalized_val = (val - self._MIN_TEMP) / self._temp_diff

        # Interpolate RGB values
        r = int(self._LOW_COLOR[0] + normalized_val * self._red)
        g = int(self._LOW_COLOR[1] + normalized_val * self._green)
        b = int(self._LOW_COLOR[2] + normalized_val * self._blue)

        # Ensure that the color values are between 0 and 255
        return color_rgb(np.clip(r, 0, 255),
                         np.clip(g, 0, 255),
                         np.clip(b, 0, 255))

    def draw_thermal_image(self, temps):
        # Draw squares to represent each pixel of the thermal image
        # for row in range(_GRID_LEN):
        for row in range(_INTRP_LEN):
            # for col in range(_GRID_LEN):
            for col in range(_INTRP_LEN):
                color = self.map_temperature(temps[row, col])
                rect = Rectangle(Point(col * self._draw_distance, row * self._draw_distance), 
                                 Point((col + 1) * self._draw_distance, (row + 1) * self._draw_distance))
                rect.setFill(color)
                rect.draw(self.win)


class ThermalCamProtocol(FerbProtocol):
    def __init__(self):
        self.wait_timer = None
        self.TIME_LIMIT = 10

        # Generate x and y coordinates for the original and interpolated Grid-EYE output
        self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
        self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
        self.interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)

        self.cam = ThermalCam()

    def data_received(self, data): # redefine this to overwrite date-time printing
        self.handle_data(data[:128])
        
        self.cancel_wait_timer()  # Cancel current wait timer
        self.start_wait_timer()  # Restart wait timer upon receiving data

    def handle_data(self, data):
        temps_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION
        
        # Check the size of our received data. This is neccessary if we run the Pico very fast,
        # as in having a sleep of < 100 ms every time we send data.
        # If we run the Pico very fat, then sometimes either the full 128 bytes will not be sent,
        # or multiple packets can be received at once, making temps_array too large.
        # Furthermore, for the current unoptimized drawing algorithm, a sleep of < 250 ms doesn't
        # show a noticable performance increase.
        if temps_array.size != 64:
            print("skipped")
            return
        
        temps_matrix = temps_array.reshape((_GRID_LEN, _GRID_LEN))

        # Create a scipy interpolation function for our temperature reading
        interp_func = RegularGridInterpolator((self.orig_coords, self.orig_coords), temps_matrix)

        # Interpolate values for the new coordinates using the interpolation function
        # and feed the interpolated matrix into the thermal cam
        self.cam.draw_thermal_image(interp_func((self.interp_Y, self.interp_X)))
        # self.cam.draw_thermal_image(temps_matrix)


    def connection_lost(self, exc):
        print(f"Connection with {self.peername} closed")
        self.cam.win.close()
        self.cancel_wait_timer()  # Cancel wait timer when connection is lost


if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(ThermalCamProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
