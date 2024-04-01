import asyncio
import numpy as np
from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION
import pygame

# Constants for Pygame visualization
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400
PIXEL_SIZE = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class GridEyeProtocol(FerbProtocol):
    def __init__(self):
        super().__init__()
        # Initialize Pygame
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Heatmap Visualization')
        self.clock = pygame.time.Clock()

        # Initialize data_history to store historical data
        self.data_history = []

    def handle_data(self, data):
        try:
            msg = data.decode()
            print(msg)

            if msg[0] == "~":
                print("Skipped")
                return
            
            # Convert the bytearray to a numpy array of 16-bit integers (short ints)
            data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

            # Reshape the array to form an 8x8 matrix
            matrix = data_array.reshape((8, 8))

            detected_blobs = self.blob_detection(matrix)
            total_count = sum(blob['person_count'] for blob in detected_blobs)
            print("Total count:", total_count)

            # Update heatmap visualization
            self.update_heatmap(matrix)

            # Append data to history
            self.data_history.append({
                'matrix': matrix,
                'blobs': detected_blobs
            })
        except Exception as e:
            print(f"error: {e}")

    def update_heatmap(self, matrix):
        # Only update if the matrix has changed
        if self.data_history and np.array_equal(matrix, self.data_history[-1]['matrix']):
            return

        # Clear the window with a black background
        self.window.fill(BLACK)

        # Determine the intensity for the entire matrix at once
        intensity_matrix = np.where(matrix > 24, 255, 0)

        # Draw the heatmap, updating only the pixels that have changed
        for x in range(8):
            for y in range(8):
                # Check if the pixel has changed
                if not self.data_history or matrix[x, y] != self.data_history[-1]['matrix'][x, y]:
                    # Determine the rectangle's position and size
                    rect_position = (x * PIXEL_SIZE, y * PIXEL_SIZE)
                    rect_size = (PIXEL_SIZE, PIXEL_SIZE)
                    # Draw a rectangle for the pixel if it has changed
                    pygame.draw.rect(self.window, (intensity_matrix[x, y], intensity_matrix[x, y], intensity_matrix[x, y]), (rect_position, rect_size))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        self.clock.tick(60)  # Adjust as needed

    def blob_detection(self, matrix):
        """
        Perform blob detection on the temperature matrix.

        Args:
        - matrix (numpy.ndarray): An 8x8 matrix of temperature values.

        Returns:
        - List of tuples: Each tuple represents the coordinates (row, column) of the detected blobs.
        """
        THRESHOLD_TEMP = 24  # Define a threshold temperature value to consider as part of a blob

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

        # Iterate through pixels of each blob
        for blob in blobs:
            pixel_count = len(blob)
            person_count = 0
            for pixel in blob:
                # Check amount of pixels in blob
                if pixel_count <= 2:
                    person_count = 1

                elif pixel_count >=3  and pixel_count <= 4:
                    person_count = 2

                elif pixel_count >= 5 and pixel_count <= 6:
                    person_count = 3

                elif pixel_count >= 7 and pixel_count <= 8:
                    person_count = 4
                
                elif pixel_count >= 9:
                    person_count = 5

            blob_data = {'coordinates': blob, 'person_count': person_count}
            # Replace the blob with its pixel count and adjusted person count
            blobs[blobs.index(blob)] = blob_data
        
        total_count = sum(blob['person_count'] for blob in blobs)
        print("Total count:", total_count)

        return blobs

if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(GridEyeProtocol))
        
    except KeyboardInterrupt:
        print("\nGoodbye cruel world\n")

    # Quit Pygame
    pygame.quit()
