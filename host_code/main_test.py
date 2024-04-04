import sys
import threading
import numpy as np
import asyncio

from FERB_GUI import FERBApp, Redirect
from scipy.interpolate import RegularGridInterpolator
from server_base import Server, FerbProtocol, PIXEL_TEMP_CONVERSION
# from thermal_cam import ThermalCam


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
GRID_EYE_HEIGHT = 52

class GridEyeProtocol(FerbProtocol):
    def __init__(self, screen_len):
        super().__init__()

        # self.app = app
        # self.cam = ThermalCam(app.canvas, screen_len)
        
        # Generate x and y coordinates for the original and interpolated Grid-EYE output
        self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
        self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
        self.interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)

        # Used for background subtraction
        self.background = np.zeros(shape=(_INTRP_LEN, _INTRP_LEN))
        
        # Variables for calibration sequence
        self.cal_finished = True
        self.cal_counter = 1

    def blob_detection(self, matrix):
        """
        Perform blob detection on the temperature matrix.

        Args:
        - matrix (numpy.ndarray): An 8x8 matrix of temperature values.

        Returns:
        - List of tuples: Each tuple represents the coordinates (row, column) of the detected blobs.
        """
        THRESHOLD_TEMP = 170  # Define a threshold temperature value to consider as part of a blob

        blobs = []
        visited = set()

        # TODO: try limiting the blob size

        # Define a function to perform depth-first search (DFS)
        def dfs(row, col, blob):
            if (row, col) in visited or row < 0 or col < 0 or row >= matrix.shape[0] or col >= matrix.shape[1]:
                return
            if matrix[row][col] < THRESHOLD_TEMP:
                return
            visited.add((row, col))
            blob.append((row, col))
            # Explore neighboring cells
            dfs(row + 1, col, blob)
            dfs(row - 1, col, blob)
            dfs(row, col + 1, blob)
            dfs(row, col - 1, blob)
            # Diagonal exploration 
            dfs(row - 1, col - 1, blob)
            dfs(row - 1, col + 1, blob)
            dfs(row + 1, col - 1, blob)
            dfs(row + 1, col + 1, blob)

        # Iterate through each cell in the matrix
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if matrix[i][j] >= THRESHOLD_TEMP and (i, j) not in visited:
                    # Start a new blob
                    blob = []
                    dfs(i, j, blob)
                    blobs.append(blob)

        pixel_per_person = self.pixel_occupancy(GRID_EYE_HEIGHT)
        print(pixel_per_person)

        # Iterate through pixels of each blob
        for blob in blobs:
            pixel_count = len(blob)
            person_count = 0
            for pixel in blob:
                # Check amount of pixels in blob
                if pixel_count < pixel_per_person * 2:
                    person_count = 1

                elif pixel_count >= pixel_per_person * 2 and pixel_count < pixel_per_person * 3:
                    person_count = 2

                elif pixel_count >= pixel_per_person * 3 and pixel_count < pixel_per_person * 4:
                    person_count = 3

                elif pixel_count >= pixel_per_person * 3.5 and pixel_count < pixel_per_person * 4.5:
                    person_count = 4

            # blob_data = {'coordinates': blob, 'person_count': person_count}
            blob_data = {'pixels': len(blob), 'person_count': person_count}
            # Replace the blob with its pixel count and adjusted person count
            blobs[blobs.index(blob)] = blob_data
        
        total_count = sum(blob['person_count'] for blob in blobs)
        print("Total count:", total_count)

        return blobs

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
            
            diff_matrix = np.clip(temperatures - self.background, _MIN_VAL, _MAX_VAL)
            
            for i in range(_INTRP_LEN):
                for j in range(_INTRP_LEN):
                    diff_matrix[i,j] = self.convert_to_grayscale(diff_matrix[i,j])

            # self.cam.draw_thermal_image(diff_matrix)

            # self.trigger_custom_event(np.random.randint(0,100))

            print("Temperature Matrix:")
            
            for row in diff_matrix:
                print('[', end='')
                print(' '.join(map(str, row[:16])), end='')
                print(']')

            print("\nDetected Blobs:")
            detected_blobs = self.blob_detection(diff_matrix)
            for i, blob in enumerate(detected_blobs, start=1):
                print(f"Blob {i}: {blob}")
            print("\n-----------------------------------------\n")
        
        except Exception as e:
            print(f"error: {e}")
    
    # def trigger_custom_event(self, data):
    #     # Trigger the custom event
    #     self.app.event_generate("<<CustomEvent>>", when="tail", data=data)
    
    def convert_to_grayscale(self, value) -> int:
        return int(((value - _MIN_VAL) / (_MAX_VAL - _MIN_VAL)) * _GRAYSCALE)
    
    def pixel_occupancy(self, height):
        # Calculated from R = 2 * x * tan(60 degrees / 2)
        # R = area in meters squared
        # x = height in meters 
        # Below is coneverted to inches 
        area = height * 45.4973

        # About the size a person takes up in inches 
        average_human_area = 80

        # Taking the detection area, divide by amount of pixels to find pixel size 
        grid_size = _INTRP_LEN * _INTRP_LEN
        pixels = area / grid_size

        # Take the area of the person and the area of a pixel and compare 
        # Obtain the amount of pixels a person should take up 
        pixel_occupancy_per_person = average_human_area / pixels

        return pixel_occupancy_per_person

# if __name__ == "__main__":
#     # Create FERB GUI App
#     app = FERBApp()

#     # Overwrite system stdout
#     # A whole section of this GUI relies in this. I hate it.
#     old_stdout = sys.stdout    
#     sys.stdout = Redirect(app.server_text)

#     server = Server(lambda:GridEyeProtocol(app, SCREEN_HEIGHT))

#     # Run GUI and server
#     threading.Thread(target=server.run).start()
#     app.mainloop()

if __name__ == "__main__":
    server = Server(lambda:GridEyeProtocol(SCREEN_HEIGHT))
    server.run()