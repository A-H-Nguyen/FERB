import numpy as np
import tkinter as tk

from scipy.interpolate import RegularGridInterpolator
from server_base import FerbProtocol, PIXEL_TEMP_CONVERSION

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

    def calibrate(self, input_matrix) -> None:
        self.background += input_matrix
        self.cal_counter += 1

        if self.cal_counter > 5:
            self.background /= 5 # Hardcode this value instead
                                 # I was using the counter for some fucking reason
            self.cal_finished = True
            self.print_timestamp("Calibration finished.")
    
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
                                  _MIN_VAL, _MAX_VAL)
            self.cam.draw_thermal_image(diff_matrix)
        
        except Exception as e:
            print(f"error: {e}")
