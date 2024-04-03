import numpy as np
import tkinter as tk


# Number of pixels for both original Grid-EYE output, and interpolated output
_GRID_LEN = 8
_INTRP_LEN = 16
_GRAYSCALE = 255

# Default values for range of temps post-background subtraction
_MIN_VAL = 0
_MAX_VAL = 5


class ThermalCam:
    def __init__(self, canvas: tk.Canvas, len):
        self._canvas = canvas
        self._resolution = len
        self._draw_len = len / _INTRP_LEN

        self.prev_image = np.zeros((_INTRP_LEN, _INTRP_LEN))

    def draw_thermal_image(self, temps):
        curr_image = np.zeros((_INTRP_LEN, _INTRP_LEN))

        for row in range(_INTRP_LEN):
            for col in range(_INTRP_LEN):
                
                if self.convert_to_grayscale(temps[row,col]) > 100:
                    color = "black"
                    curr_image[row,col] = 1
                else:
                    color = "white"
                    curr_image[row,col] = 0

                if curr_image[row,col] == self.prev_image[row,col]:
                    pass
                
                self.prev_image[row,col] = curr_image[row,col]

                x0 = col * self._draw_len
                y0 = row * self._draw_len
                x1 =  x0 + self._draw_len
                y1 =  y0 + self._draw_len

                self._canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='')

    def convert_to_grayscale(self, value) -> int:
        return int(((value - _MIN_VAL) / (_MAX_VAL - _MIN_VAL)) * _GRAYSCALE)


