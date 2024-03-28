import asyncio
import numpy as np

from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION
from scipy.interpolate import RegularGridInterpolator

# Number of pixels for both original Grid-EYE output, and interpolated output
_GRID_LEN = 8
_INTRP_LEN = 16

THRESHOLD_TEMP = 24  # Define a threshold temperature value to consider as part of a blob


class Blob:
    def __init__(self, label: int) -> None:
        self.pixels = []
        self.label = label

        # Minimum and maximum blob sizes, assuming that the blob is a square
        self.min = 4  # minimum blob size is a 2x2
        self.max = 16 # maximum blob size is a 4x4

    def add_pixel(self, new_pixel) -> None:
        self.pixels.append(new_pixel)


class GridEyeProtocol(FerbProtocol):
    def __init__(self):
        self.wait_timer = None
        self.TIME_LIMIT = 10

        # Generate x and y coordinates for the original and interpolated Grid-EYE output
        self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
        self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
        self.interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)

        self.visited_matrix = np.zeros(shape=(_INTRP_LEN, _INTRP_LEN))
        self.blobs = []

    def handle_data(self, data):
        # Convert the bytearray to a numpy array of 16-bit integers (short ints)
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

        if data_array.size != 64:
            print("skipped")
            return

        # Reshape the array to form an 8x8 matrix
        matrix = data_array.reshape((_GRID_LEN, _GRID_LEN))

        # Create a scipy interpolation function for our temperature reading
        interp_func = RegularGridInterpolator((self.orig_coords, self.orig_coords), matrix)
        interp_matrix = interp_func((self.interp_Y, self.interp_X))
        norm_matrix = np.where(interp_matrix > THRESHOLD_TEMP, interp_matrix, 0)

        print("Temperature Matrix:")
        print(norm_matrix)
        print("\nDetected Blobs:")
        # detected_blobs = self.blob_detection(matrix)
        detected_blobs = self.blob_detection(interp_matrix)
        for i, blob in enumerate(detected_blobs, start=1):
            print(f"Blob {i}: {blob}")
        print("\n-----------------------------------------\n")
        
    def blob_detection(self, temps):
        """
        Perform blob detection on the temperature matrix.

        Args:
        - temps (numpy.ndarray): An 8x8 matrix of temperature values.

        Returns:
        - List of tuples: Each tuple represents the coordinates (row, column) of the detected blobs.
        """

        self.visited_matrix &= 0

        # blobs = []
        # visited = set()

        # Iterate through each cell in the matrix
        for i in range(_INTRP_LEN):
            for j in range(_INTRP_LEN):
                # if temps[i][j] >= THRESHOLD_TEMP and (i, j) not in visited:
                if temps[i,j] >= THRESHOLD_TEMP and not self.visited_matrix[i,j]:

                    # Check if this pixel is not already wrapped in a blob
                    for b in self.blobs:
                        pass

                    # Start a new blob
                    new_blob = Blob(len(self.blobs))

                    self.blobs.append(new_blob)
                    # blob = []
                    # dfs(i, j, blob)
                    # blobs.append(blob)

        # # Define a function to perform depth-first search (DFS)
        # def dfs(row, col, blob):
        #     if (row, col) in visited or row < 0 or col < 0 or row >= temps.shape[0] or col >= matrix.shape[1]:
        #         return
        #     if matrix[row][col] < THRESHOLD_TEMP:
        #         return
        #     visited.add((row, col))
        #     blob.append((row, col))
        #     # Explore neighboring cells
        #     dfs(row + 1, col, blob)
        #     dfs(row - 1, col, blob)
        #     dfs(row, col + 1, blob)
        #     dfs(row, col - 1, blob)
        #     # Diagonal exploration 
        #     dfs(row - 1, col - 1, blob)
        #     dfs(row - 1, col + 1, blob)
        #     dfs(row + 1, col - 1, blob)
        #     dfs(row + 1, col + 1, blob)

        # # Iterate through each cell in the matrix
        # for i in range(matrix.shape[0]):
        #     for j in range(matrix.shape[1]):
        #         if matrix[i][j] >= THRESHOLD_TEMP and (i, j) not in visited:
        #             # Start a new blob
        #             blob = []
        #             dfs(i, j, blob)
        #             blobs.append(blob)

        # return blobs

    def dfs(self, row, col, temps, blob: Blob):
        # Check bounds
        if row < 0 or col < 0 or row >= _INTRP_LEN or col >= _INTRP_LEN:
            return

        # Check if this location has already been visited
        if self.visited_matrix[row,col]: 
            return

        self.visited_matrix[row,col] = 1

        # Check pixel value
        if temps[row, col] < THRESHOLD_TEMP:
            return 

        blob.add_pixel((row,col))

        # Visit surrounding pixels
        self.dfs(row, col - 1, blob)
        self.dfs(row, col + 1, blob)
        self.dfs(row - 1, col, blob)
        self.dfs(row - 1, col - 1, blob)
        self.dfs(row - 1, col + 1, blob)
        self.dfs(row + 1, col, blob)
        self.dfs(row + 1, col - 1, blob)
        self.dfs(row + 1, col + 1, blob)

if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(GridEyeProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")

