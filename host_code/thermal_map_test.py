import asyncio
import numpy as np
import plotly.graph_objects as go
from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION

class GridEyeProtocol(FerbProtocol):
    def __init__(self):
        super().__init__()
        self.data_history = []

    def handle_data(self, data):
        msg = data.decode()

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

        # Append data to history
        self.data_history.append({
            'matrix': matrix,
            'blobs': detected_blobs
        })

        # Update heatmap
        self.update_heatmap()

    def update_heatmap(self):
        # Extract data from history for heatmap
        matrix = self.data_history[-1]['matrix']

        # Create heatmap figure
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            colorscale='Viridis',
            zmin=np.min(matrix),
            zmax=np.max(matrix)
        ))

        fig.update_layout(
            title='Live Heatmap of Temperature',
            xaxis_title='Column',
            yaxis_title='Row'
        )

        # Show the figure
        fig.show()

    def blob_detection(self, matrix):
        """
        Perform blob detection on the temperature matrix.

        Args:
        - matrix (numpy.ndarray): An 8x8 matrix of temperature values.

        Returns:
        - List of dictionaries: Each dictionary represents the blob with its coordinates and person count.
        """
        THRESHOLD_TEMP = 24  # Define a threshold temperature value to consider as part of a blob

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

            blob_data = {'coordinates': blob, 'person_count': person_count}
            # Replace the blob with its pixel count and adjusted person count
            blobs[blobs.index(blob)] = blob_data
        
        return blobs

if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(GridEyeProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
