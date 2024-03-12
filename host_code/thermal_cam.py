import asyncio
import numpy as np

from graphics import *
from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION
from scipy.interpolate import RegularGridInterpolator


_GRID_LEN = 8
_INTRP_LEN = 16
_RESOLUTION = 400

class ThermalCam:
    def __init__(self) -> None:
        # Define the size of the thermal image grid (8x8 for Grid-EYE)
        self.win = GraphWin("Thermal Image", _RESOLUTION, _RESOLUTION)

    def map_temperature(self, value):
        # Define colors for different temperature ranges
        ambient_temp = 22
        person_temp = 23

        if value < ambient_temp:            
            return color_rgb(0, 255, 0) # green
        
        elif value > person_temp:
            return color_rgb(255, 0, 0) # red
        
        else:
            return color_rgb(255, 255, 0) # yellow

    def draw_thermal_image(self, temps):
        length, width = temps.shape

        # Draw squares to represent each pixel of the thermal image
        for row in range(length):
            for col in range(width):
                color = self.map_temperature(temps[row, col])
                rect = Rectangle(Point(col * (_RESOLUTION/width), row * (_RESOLUTION/length)), 
                                 Point((col + 1) * (_RESOLUTION/width), (row + 1) * (_RESOLUTION/length)))
                rect.setFill(color)
                rect.draw(self.win)


class ThermalCamProtocol(FerbProtocol):
    def __init__(self):
        self.wait_timer = None
        self.TIME_LIMIT = 10

        # Generate x and y coordinates for the original and interpolated Grid-EYE output
        self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
        self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
        self.new_X, self.new_Y = np.meshgrid(self.new_coords, self.new_coords)

        self.cam = ThermalCam()

    def data_received(self, data): # redefine this to overwrite date-time printing
        self.handle_data(data)
        
        self.cancel_wait_timer()  # Cancel current wait timer
        self.start_wait_timer()  # Restart wait timer upon receiving data

    def handle_data(self, data):
        temps_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION
        temps_matrix = temps_array.reshape((_GRID_LEN, _GRID_LEN))
        temps_interp = self.interp(temps_matrix)

        self.cam.draw_thermal_image(temps_interp)
    
    def interp(self, _grid):
        # Create RegularGridInterpolator
        interp_func = RegularGridInterpolator((self.orig_coords, self.orig_coords), _grid)

        # Interpolate values for the new coordinates using RegularGridInterpolator
        resized_matrix = interp_func((self.new_Y, self.new_X))

        return resized_matrix


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
