import threading
import numpy as np
import tkinter as tk

from blob_detect import BlobDetector
from FERB_GUI import FERBApp, curr_cam # AAAAAAAAAAAAAAH FUCK YOU
from scipy.interpolate import RegularGridInterpolator
from server_base import Server, FerbProtocol, PIXEL_TEMP_CONVERSION

# Number of pixels for both original Grid-EYE output, and interpolated output
_GRID_LEN = 8  # Number of pixels for both original Grid-EYE output
_INTRP_LEN = 16  # Number of pixels for interpolated output
_GRAYSCALE = 255  # Maximum value for grayscale representation

_MIN_VAL = 0  # Minimum value for temperature range
_MAX_VAL = 5  # Maximum value for temperature range

# Width and Height of the Raspberry Pi screen
SCREEN_WIDTH = 800  
SCREEN_HEIGHT = 400 

# Constants related to thermal camera and blob detection
GRID_EYE_HEIGHT = 10  # Height of the Grid-EYE sensor
HUMAN_AREA = 80  # Area occupied by a human (in pixels)
THRESHOLD_TEMP = 170  # Threshold temperature for blob detection


class GridEyeProtocol(FerbProtocol):
    def __init__(self, app: FERBApp):
        super().__init__()

        self.app = app
        
        # Generate x and y coordinates for original and interpolated Grid-EYE output
        self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
        self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
        self.interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)

        self.background = np.zeros(shape=(_INTRP_LEN, _INTRP_LEN))
        self.cal_counter = 0
        self.blob_detector = BlobDetector()

    def prep_calibration(self):
        self.print_timestamp(f"Calibrating sensor...")
        print("Get the fuck out of the way!!!!")
        
        self._cal = True
        self.background = np.zeros(shape=(_INTRP_LEN, _INTRP_LEN))

    def calibrate(self, data):
        """
        Calibration process: accumulating background data
        """
        self.background += data
        self.cal_counter += 1

        if self.cal_counter == 5:
            # Calculate average background reading
            self.background /= self.cal_counter
            
            self.cal_counter = 0
            self._cal = False
          
            self.print_timestamp("Calibration finished.")
    
    def handle_data(self, data):
        # Convert the bytearray to a numpy array of 16-bit integers (short ints)
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION
        thermal_image = data_array.reshape((8, 8))
        interp_func = RegularGridInterpolator((self.orig_coords, self.orig_coords), 
                                              thermal_image)
        temperature_matrix = interp_func((self.interp_Y, self.interp_X))

        if self._cal:
            # If in calibration mode, accumulate background data
            self.calibrate(temperature_matrix)
            return

        # Background subtraction
        diff_matrix = np.clip(temperature_matrix - self.background, 
                              _MIN_VAL, _MAX_VAL)
        
        # Convert temperature differences to grayscale
        for i in range(_INTRP_LEN):
            for j in range(_INTRP_LEN):
                diff_matrix[i,j] = self.convert_to_grayscale(diff_matrix[i,j])

        detected_blobs, count = self.blob_detector.blob_detection(diff_matrix)
        self.app.update_client_person_count(self.client_id, count)
        
        # interp_func = RegularGridInterpolator((self.orig_coords, 
        #                                        self.orig_coords), temperature_matrix)

        # difference_matrix = np.clip(temperature_matrix - self.background, 
        #                             _MIN_VAL, _MAX_VAL)
        
        # temp_intrp = interp_func((self.interp_Y, self.interp_X))
        
        # if not self.cal_finished:
        #     self.calibrate(temp_intrp)
        #     return
        
        # difference_matrix = np.clip(np.round(temp_intrp - self.background), _MIN_VAL, _MAX_VAL)
        
        global curr_cam
        if curr_cam == self.client_id:
            self.app.draw_image(temperature_matrix)

    
    def convert_to_grayscale(self, value) -> int:
        # Convert temperature difference to grayscale value
        return int(((value - _MIN_VAL) / (_MAX_VAL - _MIN_VAL)) * _GRAYSCALE)


    def connection_made(self, transport):
        """
        When a new FERB connects, automatically switch to its thermal cam.
        IDK why, I thought it would be cool. I guess.
        """
        super().connection_made(transport)
        self.app.add_client(self.client_id)
        
        global curr_cam 
        curr_cam = self.client_id 


    def connection_lost(self, exc):
        super().connection_lost(exc)
        self.app.remove_client(self.client_id)



#def draw_me():
 #   print("AAAAAA")


if __name__ == "__main__":
    # Create FERB GUI App
    app = FERBApp()
    app.add_client(420)
    app.add_client(69)
    # server = Server(lambda:GridEyeProtocol(app))

    # Run GUI and server
   # threang.Thread(target=server.run).start()
    app.mainloop()

