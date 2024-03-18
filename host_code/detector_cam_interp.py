import asyncio
import numpy as np

from graphics import *
from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION
from scipy.interpolate import RegularGridInterpolator

# Number of pixels for both original Grid-EYE output, and interpolated output
_GRID_LEN = 8
_INTRP_LEN = 16

THRESHOLD_TEMP = 24  # Define a threshold temperature value to consider as part of a blob


class ThermalCam:
    def __init__(self, resolution=400, min_temp=15, max_temp=30, 
                 low_color=(77, 255, 195), high_color=(255, 0, 0)) -> None:
        # Define the size of the thermal image grid
        self._RESOLUTION = resolution

        # Set the window with the given resolution
        self.win = GraphWin("Thermal Image", self._RESOLUTION, self._RESOLUTION)

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
        # Draw squares to represent each pixel of the thermal image
        # for row in range(_GRID_LEN):
        for row in range(_INTRP_LEN):
            # for col in range(_GRID_LEN):
            for col in range(_INTRP_LEN):
                color = self.map_temperature(temps[row, col])
                rect = Rectangle(Point(col * self._draw_distance, row * self._draw_distance), 
                                 Point((col + 1) * self._draw_distance, (row + 1) * self._draw_distance))
                rect.setFill(color)
                rect.draw(self.win)


class GridEyeProtocol(FerbProtocol):
    def __init__(self):
        self.wait_timer = None
        self.TIME_LIMIT = 10

        # Generate x and y coordinates for the original and interpolated Grid-EYE output
        self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
        self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
        self.interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)

        self.cam = ThermalCam()

    def handle_data(self, data):
        # Convert the bytearray to a numpy array of 16-bit integers (short ints)
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

        if data_array.size != 64:
            print("skipped")
            return

        # Normalization
        # for i in range(data_array.size):
        #     if data_array[i] < THRESHOLD_TEMP:
        #         data_array[i] = 0

        # Reshape the array to form an 8x8 matrix
        matrix = data_array.reshape((_GRID_LEN, _GRID_LEN))

        # Create a scipy interpolation function for our temperature reading
        interp_func = RegularGridInterpolator((self.orig_coords, self.orig_coords), matrix)
        interp_matrix = interp_func((self.interp_Y, self.interp_X))

        for i in range(_INTRP_LEN ):
            for j in range(_INTRP_LEN ):
                if interp_matrix[i][j] < THRESHOLD_TEMP:
                    interp_matrix[i][j] = 0

        print("Temperature Matrix:")
        print(interp_matrix)
        print("\nDetected Blobs:")
        # detected_blobs = self.blob_detection(matrix)
        detected_blobs = self.blob_detection(interp_matrix)
        for i, blob in enumerate(detected_blobs, start=1):
            print(f"Blob {i}: {blob}")
        print("\n-----------------------------------------\n")
        
        # self.cam.draw_thermal_image(matrix)
        self.cam.draw_thermal_image(interp_matrix)

    def blob_detection(self, matrix):
        """
        Perform blob detection on the temperature matrix.

        Args:
        - matrix (numpy.ndarray): An 8x8 matrix of temperature values.

        Returns:
        - List of tuples: Each tuple represents the coordinates (row, column) of the detected blobs.
        """

        blobs = []
        visited = set()

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

        return blobs


if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(GridEyeProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")

