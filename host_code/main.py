import sys
import threading
import numpy as np

from FERB_GUI import FERBApp, Redirect
from scipy.interpolate import RegularGridInterpolator
from server_base import Server, FerbProtocol, PIXEL_TEMP_CONVERSION
from thermal_cam import ThermalCam


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
    def __init__(self, app: FERBApp, screen_len):
        super().__init__()

        self.app = app
        self.cam = ThermalCam(app.canvas, screen_len)
        
        # Generate x and y coordinates for the original and interpolated Grid-EYE output
        self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
        self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
        self.interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)

        # Used for background subtraction
        # self.background = np.zeros(shape=(_INTRP_LEN, _INTRP_LEN))
        self.background = np.zeros(shape=(_GRID_LEN, _GRID_LEN))
        
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
            temp_array = data_array.reshape((8,8))
            
            if not self.cal_finished:
                self.calibrate(temp_array)
                return
           
            diff_matrix = np.clip(np.round(temp_array - self.background), _MIN_VAL, _MAX_VAL)
            self.cam.draw_thermal_image(diff_matrix)
            
            # interp_func = RegularGridInterpolator((self.orig_coords, 
            #                                        self.orig_coords), temp_array)
            # temp_intrp = interp_func((self.interp_Y, self.interp_X))
            
            # if not self.cal_finished:
            #     self.calibrate(temp_intrp)
            #     return
            
            # diff_matrix = np.clip(np.round(temp_intrp - self.background), _MIN_VAL, _MAX_VAL)

            self.trigger_custom_event(np.random.randint(0,100))
        
        except Exception as e:
            print(f"error: {e}")
    
    def trigger_custom_event(self, data):
        # Trigger the custom event
        self.app.event_generate("<<CustomEvent>>", when="tail", data=data)


if __name__ == "__main__":
    # Create FERB GUI App
    app = FERBApp()

    # Overwrite system stdout
    # A whole section of this GUI relies in this. I hate it.
    old_stdout = sys.stdout    
    sys.stdout = Redirect(app.server_text)

    server = Server(lambda:GridEyeProtocol(app, SCREEN_HEIGHT))

    # Run GUI and server
    threading.Thread(target=server.run).start()
    app.mainloop()