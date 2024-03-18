import numpy as np
import random as rand

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

        # Create the Rectangle objects for thermal image once
        self.rectangles = []
        for row in range(_INTRP_LEN):
            tmp_array = []
            for col in range(_INTRP_LEN):
                rect = Rectangle(Point(0, 0), Point(0, 0))  # Create a dummy rectangle
                tmp_array.append(rect)
            self.rectangles.append(tmp_array)
        # self.curr_temps = np.zeros((16,16), dtype=np.uint16)

        # Set the window with the given resolution
        self.win = GraphWin("Thermal Image", self._RESOLUTION, self._RESOLUTION)
        # self.win.setBackground(color_rgb(self._LOW_COLOR))
        # self.draw_thermal_image(self.curr_temps)

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
        for row in range(_INTRP_LEN):
            for col in range(_INTRP_LEN):
                # temp = temps[row, col]

                # if not temp > 1:
                #     continue
                # #     color = self.map_temperature(temp)
                # # else:
                # #     color = color_rgb(*self._LOW_COLOR)
                # color = self.map_temperature(temp)

                # rect = Rectangle(Point(col * self._draw_distance, row * self._draw_distance), 
                #                  Point((col + 1) * self._draw_distance, (row + 1) * self._draw_distance))
                
                # # rect = self.cam_pixels[row][col]
                # color = self.map_temperature(temps[row, col])
                
                # rect.setFill(color)
                # rect.draw(self.win)

                # self.rect.move(col * self._draw_distance, row * self._draw_distance)
                # self.rect.setFill(color)
                # self.rect.draw(self.win)
                
                # rect_index = row * _INTRP_LEN + col
                # rect = self.rectangles[rect_index]
                rect = self.rectangles[row][col]

                temp = temps[row, col]

                if temp > 1:
                    color = self.map_temperature(temp)
                else:
                    color = color_rgb(*self._LOW_COLOR)

                # color = self.map_temperature()
                
                rect.setFill(color)

                # Update rectangle position and size
                # rect.getP1().setX(col * self._draw_distance)
                # rect.getP1().setY(row * self._draw_distance)
                # rect.getP2().setX((col + 1) * self._draw_distance)
                # rect.getP2().setY((row + 1) * self._draw_distance)
                p1 = rect.getP1()

                # Draw the rectangle if it's not already drawn
                if not rect.isDrawn():
                    rect.draw(self.win)

def value_gen():



if __name__ == "__main__":
    orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
    new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
    interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)
    cam = ThermalCam(min_temp=0, max_temp=10)

