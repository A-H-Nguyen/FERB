import numpy as np

from scipy.interpolate import RegularGridInterpolator
from server_base import Server, FerbProtocol, PIXEL_TEMP_CONVERSION

# Constants defining various parameters
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


class BlobDetector:
    def __init__(self):
        # Calculate pixel occupancy per person based on height
        self.pixel_per_person = self.pixel_occupancy(GRID_EYE_HEIGHT)

    def blob_detection(self, matrix):
        blobs = []
        visited = set()

        # Depth-first search for blob detection
        def dfs(row, col, blob):
            # Base cases for DFS termination
            if (row, col) in visited or row < 0 or col < 0 or row >= matrix.shape[0] or col >= matrix.shape[1]:
                return
            if matrix[row][col] < THRESHOLD_TEMP:
                return
            
            # Mark pixel as visited and add to blob
            visited.add((row, col))
            blob.append((row, col))

            # Recursive calls for neighboring pixels
            dfs(row + 1, col, blob)
            dfs(row - 1, col, blob)
            dfs(row, col + 1, blob)
            dfs(row, col - 1, blob)
            dfs(row - 1, col - 1, blob)
            dfs(row - 1, col + 1, blob)
            dfs(row + 1, col - 1, blob)
            dfs(row + 1, col + 1, blob)

        # Iterate over the matrix for blob detection
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if matrix[i][j] >= THRESHOLD_TEMP and (i, j) not in visited:
                    blob = []
                    dfs(i, j, blob)
                    blobs.append(blob)

        # Analyze detected blobs and count persons
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

            # Store blob data with pixel count and person count
            blob_data = {'pixels': len(blob), 'person_count': person_count}
            blobs[blobs.index(blob)] = blob_data
        
        # Calculate total person count
        total_count = sum(blob['person_count'] for blob in blobs)
        print('Total Count:', total_count)
        return blobs, total_count

    def pixel_occupancy(self, height):
        # Calculate pixel occupancy per person based on height and area
        area = height * 45.4973  # Assuming an average human area
        grid_size = _INTRP_LEN * _INTRP_LEN  # Total grid size
        pixels = area / grid_size  # Pixels occupied per unit area
        pixel_occupancy_per_person = HUMAN_AREA / pixels  # Pixels occupied per person
        return pixel_occupancy_per_person

# Custom protocol for handling data from the GridEye sensor
class BlobDetectionProtocol(FerbProtocol):
    def __init__(self, screen_len):
        super().__init__()
        # Define original and interpolated coordinates
        self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
        self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
        self.interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)
        self.background = np.zeros(shape=(_INTRP_LEN, _INTRP_LEN))
        self.cal_counter = 0
        self.blob_detector = BlobDetector()

    def prep_calibration(self):
        # Prepare for calibration process
        self.print_timestamp(f"Calibrating sensor...")
        print("Get the fuck out of the way!!!!")
        self._cal = True
        self.background = np.zeros(shape=(_INTRP_LEN, _INTRP_LEN))

    def calibrate(self, data):
        # Calibration process: accumulating background data
        self.background += data
        self.cal_counter += 1

        if self.cal_counter == 5:
            # Calculate average background data
            self.background /= self.cal_counter
            self.cal_counter = 0
            self._cal = False
            self.print_timestamp("Calibration finished.")

    def handle_data(self, data):
        # Process incoming data from the sensor
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION
        interp_func = RegularGridInterpolator((self.orig_coords, self.orig_coords), data_array.reshape((8, 8)))
        temperature_matrix = interp_func((self.interp_Y, self.interp_X))

        if self._cal:
            # If in calibration mode, accumulate background
            self.calibrate(temperature_matrix)
            return

        # Compute temperature differences after background subtraction
        diff_matrix = np.clip(temperature_matrix - self.background, _MIN_VAL, _MAX_VAL)

        # Convert temperature differences to grayscale
        for i in range(_INTRP_LEN):
            for j in range(_INTRP_LEN):
                diff_matrix[i,j] = self.convert_to_grayscale(diff_matrix[i,j])

        print("Temperature Matrix:")
        for row in diff_matrix:
            print(' '.join(map(str, row)))

        # Detect blobs and count persons
        print("\nDetected Blobs:")
        detected_blobs, count = self.blob_detector.blob_detection(diff_matrix)
        for i, blob in enumerate(detected_blobs, start=1):
            print(f"Blob {i}: {blob}")
        print("\n-----------------------------------------\n")
    
    def convert_to_grayscale(self, value) -> int:
        # Convert temperature difference to grayscale value
        return int(((value - _MIN_VAL) / (_MAX_VAL - _MIN_VAL)) * _GRAYSCALE)

if __name__ == "__main__":
    # Start the server with the custom GridEyeProtocol
    server = Server(lambda:BlobDetectionProtocol(SCREEN_HEIGHT))
    server.run()
