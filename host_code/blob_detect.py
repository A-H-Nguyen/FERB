import sys
import threading
import numpy as np
import asyncio
import queue

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

data_queue = queue.Queue()
lock = threading.Lock()  # Create a lock

class BlobDetector:
    def __init__(self):
        self.pixel_per_person = self.pixel_occupancy(GRID_EYE_HEIGHT)

    def blob_detection(self, matrix):
        THRESHOLD_TEMP = 170
        blobs = []
        visited = set()

        def dfs(row, col, blob):
            if (row, col) in visited or row < 0 or col < 0 or row >= matrix.shape[0] or col >= matrix.shape[1]:
                return
            if matrix[row][col] < THRESHOLD_TEMP:
                return
            visited.add((row, col))
            blob.append((row, col))
            dfs(row + 1, col, blob)
            dfs(row - 1, col, blob)
            dfs(row, col + 1, blob)
            dfs(row, col - 1, blob)
            dfs(row - 1, col - 1, blob)
            dfs(row - 1, col + 1, blob)
            dfs(row + 1, col - 1, blob)
            dfs(row + 1, col + 1, blob)

        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if matrix[i][j] >= THRESHOLD_TEMP and (i, j) not in visited:
                    blob = []
                    dfs(i, j, blob)
                    blobs.append(blob)

        for blob in blobs:
            pixel_count = len(blob)
            person_count = 0
            for pixel in blob:
                if pixel_count < self.pixel_per_person * 2:
                    person_count = 1
                elif pixel_count >= self.pixel_per_person * 2 and pixel_count < self.pixel_per_person * 3:
                    person_count = 2
                elif pixel_count >= self.pixel_per_person * 3 and pixel_count < self.pixel_per_person * 4:
                    person_count = 3
                elif pixel_count >= self.pixel_per_person * 4 and pixel_count < self.pixel_per_person * 5:
                    person_count = 4
            blob_data = {'pixels': len(blob), 'person_count': person_count}
            blobs[blobs.index(blob)] = blob_data
        
        total_count = sum(blob['person_count'] for blob in blobs)
        return blobs

    def pixel_occupancy(self, height):
        area = height * 45.4973
        average_human_area = 80
        grid_size = _INTRP_LEN * _INTRP_LEN
        pixels = area / grid_size
        pixel_occupancy_per_person = average_human_area / pixels
        return pixel_occupancy_per_person

class GridEyeProtocol(FerbProtocol):
    def __init__(self, screen_len):
        super().__init__()
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
        self.background += data
        self.cal_counter += 1

        if self.cal_counter == 5:
            self.background /= self.cal_counter
            
            self.cal_counter = 0
            self._cal = False
          
            self.print_timestamp("Calibration finished.")

    def handle_data(self, data):
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION
        interp_func = RegularGridInterpolator((self.orig_coords,
                                                self.orig_coords),
                                               data_array.reshape((8, 8)))
        temperature_matrix = interp_func((self.interp_Y, self.interp_X))

        if self._cal:
            self.calibrate(temperature_matrix)
            return

        diff_matrix = np.clip(temperature_matrix - self.background, _MIN_VAL, _MAX_VAL)

        for i in range(_INTRP_LEN):
            for j in range(_INTRP_LEN):
                diff_matrix[i,j] = self.convert_to_grayscale(diff_matrix[i,j])

        print("Temperature Matrix:")
        for row in diff_matrix:
            print(' '.join(map(str, row)))

        print("\nDetected Blobs:")
        detected_blobs = self.blob_detector.blob_detection(diff_matrix)
        for i, blob in enumerate(detected_blobs, start=1):
            print(f"Blob {i}: {blob}")
        print("\n-----------------------------------------\n")
    
    def convert_to_grayscale(self, value) -> int:
        return int(((value - _MIN_VAL) / (_MAX_VAL - _MIN_VAL)) * _GRAYSCALE)

if __name__ == "__main__":
    server = Server(lambda:GridEyeProtocol(SCREEN_HEIGHT))
    server.run()