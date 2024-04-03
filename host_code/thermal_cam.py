import numpy as np
import tkinter as tk


# Number of pixels for both original Grid-EYE output, and interpolated output
_GRID_LEN = 8
# _INTRP_LEN = 16
_GRAYSCALE = 255

# Default values for range of temps post-background subtraction
_MIN_VAL = 0
_MAX_VAL = 5


class ThermalCam:
    def __init__(self, canvas: tk.Canvas, len):
        self._canvas = canvas
        self._resolution = len
        self._draw_len = len / _GRID_LEN

        self.prev_image = np.zeros((_GRID_LEN, _GRID_LEN), dtype=int)
        self.curr_image = np.zeros((_GRID_LEN, _GRID_LEN), dtype=int)

    def draw_thermal_image(self, temps):

        for row in range(_GRID_LEN):
            for col in range(_GRID_LEN):
                
                self.curr_image[row,col] = self.convert_to_grayscale(temps[row,col])
                color = f'#{self.curr_image[row,col]:02x}{self.curr_image[row,col]:02x}{self.curr_image[row,col]:02x}'

                if self.curr_image[row,col] == self.prev_image[row,col]:
                    pass
                
                self.prev_image[row,col] = self.curr_image[row,col]

                x0 = col * self._draw_len
                y0 = row * self._draw_len
                x1 =  x0 + self._draw_len
                y1 =  y0 + self._draw_len

                self._canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='')

    def convert_to_grayscale(self, value) -> int:
        return int(((value - _MIN_VAL) / (_MAX_VAL - _MIN_VAL)) * _GRAYSCALE)

# class ThermalCam(tk.Canvas):
#     def __init__(self, master, len, grid_len, min_val, max_val, grayscale):
#         super().__init__(master, width=len, height=len)
#         self._resolution = len
#         self._grid_len = grid_len
#         self._draw_len = len / grid_len
#         self._min_val = min_val
#         self._max_val = max_val
#         self._grayscale = grayscale

#         self.prev_image = np.zeros((grid_len, grid_len), dtype=int)
#         self.curr_image = np.zeros((grid_len, grid_len), dtype=int)

#     def draw_thermal_image(self, temps):
#         for row in range(self._grid_len):
#             for col in range(self._grid_len):
#                 self.curr_image[row, col] = self.convert_to_grayscale(temps[row, col])
#                 color = f'#{self.curr_image[row, col]:02x}{self.curr_image[row, col]:02x}{self.curr_image[row, col]:02x}'

#                 if self.curr_image[row, col] == self.prev_image[row, col]:
#                     continue
                
#                 self.prev_image[row, col] = self.curr_image[row, col]

#                 x0 = col * self._draw_len
#                 y0 = row * self._draw_len
#                 x1 = x0 + self._draw_len
#                 y1 = y0 + self._draw_len

#                 self.create_rectangle(x0, y0, x1, y1, fill=color, outline='')

#     def convert_to_grayscale(self, value):
#         return int(((value - self._min_val) / (self._max_val - self._min_val)) * self._grayscale)

