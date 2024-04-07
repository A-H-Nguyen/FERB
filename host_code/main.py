import sys
import threading
import numpy as np
import tkinter as tk

from FERB_GUI import FERBApp, curr_cam # AAAAAAAAAAAAAAH FUCK YOU
from scipy.interpolate import RegularGridInterpolator
from server_base import Server, FerbProtocol, PIXEL_TEMP_CONVERSION
from blob_detect import BlobDetector


# Number of pixels for both original Grid-EYE output, and interpolated output
_GRID_LEN = 8
_INTRP_LEN = 16
_GRAYSCALE = 255

# Default values for range of temps post-background subtraction
_MIN_VAL = 0
_MAX_VAL = 5

# Width and Height of the Raspberry Pi screen
SCREEN_WIDTH = 800  
SCREEN_HEIGHT = 400 


class GridEyeProtocol(FerbProtocol):
    def __init__(self, app: FERBApp):
        super().__init__()

        self.app = app
        
        # Generate x and y coordinates for original and interpolated Grid-EYE output
        self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
        self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
        self.interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)

        # self.background = np.zeros(shape=(_INTRP_LEN, _INTRP_LEN))
        self.background = np.zeros(shape=(_GRID_LEN, _GRID_LEN))
        self.cal_counter = 0

    def prep_calibration(self):
        self.print_timestamp(f"Calibrating sensor...")
        print("Get the fuck out of the way!!!!")
        
        self._cal = True
        self.background = np.zeros(shape=(_GRID_LEN, _GRID_LEN))

    def calibrate(self, data):
        self.background += data
        self.cal_counter += 1

        if self.cal_counter == 5:
            self.background /= self.cal_counter
            
            self.cal_counter = 0
            self._cal = False
          
            self.print_timestamp("Calibration finished.")
    
    def handle_data(self, data):
        # Convert the bytearray to a numpy array of 16-bit integers (short ints)
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

        # Reshape the array to form an 8x8 matrix
        temperature_matrix = data_array.reshape((8,8))
        if self._cal:
            self.calibrate(temperature_matrix)
            return
        
        global curr_cam
        if curr_cam == self.client_id:
            self.app.draw_image(temperature_matrix)
##########################################################
        hot_pixel = 0
        for i in range(8):
            for j in range(8):
                if temperature_matrix[i,j] > hot_pixel:
                    hot_pixel = temperature_matrix[i,j]
            if hot_pixel >= 22:
                msg = "Person Detected"
            else:
                msg = "___"

            self.gui.scrollable_frame.get_frame(self.client_id).update_status(msg)
        
        blobDetector = BlobDetector()
        blobDetector()

###########################################################

            # print("NIce matrix bRO")

        # interp_func = RegularGridInterpolator((self.orig_coords, 
        #                                        self.orig_coords), temperature_matrix)

        # difference_matrix = np.clip(temperature_matrix - self.background, 
        #                             _MIN_VAL, _MAX_VAL)
        
        # temp_intrp = interp_func((self.interp_Y, self.interp_X))
        
        # if not self.cal_finished:
        #     self.calibrate(temp_intrp)
        #     return
        
        # difference_matrix = np.clip(np.round(temp_intrp - self.background), _MIN_VAL, _MAX_VAL)

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

