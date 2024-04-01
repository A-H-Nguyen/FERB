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
        # Clear the window with a black background
        self.window.fill(BLACK)

        # Determine the intensity for the entire matrix at once
        intensity_matrix = np.where(matrix > 24, 255, 0)

        # Draw the heatmap
        for x in range(8):
            for y in range(8):
                # Determine the rectangle's position and size
                rect_position = (x * PIXEL_SIZE, y * PIXEL_SIZE)
                rect_size = (PIXEL_SIZE, PIXEL_SIZE)
                # Draw a rectangle for the pixel
                pygame.draw.rect(self.window, (intensity_matrix[x, y], intensity_matrix[x, y], intensity_matrix[x, y]), (rect_position, rect_size))

        # Update the display
        pygame.display.flip()

    def blob_detection(self, matrix):
        # Your blob detection code here...
        pass

if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(GridEyeProtocol))

        # Initialize the Pygame event loop
        pygame.init()
        running = True

        # Main Pygame event loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

    except KeyboardInterrupt:
        print("\nGoodbye cruel world\n")

    # Quit Pygame
    pygame.quit()

