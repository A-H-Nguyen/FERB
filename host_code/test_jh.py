import asyncio
import numpy as np
import tkinter as tk
from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION

# Constants for visualization
PIXEL_SIZE = 50
WHITE = "#FFFFFF"
RED = "#FF0000"
BLACK = "#000000"

class GridEyeProtocol(FerbProtocol):
    def __init__(self):
        super().__init__()
        self.root = tk.Tk()
        self.root.title("Heatmap Visualization")

        self.canvas = tk.Canvas(self.root, width=PIXEL_SIZE * 8, height=PIXEL_SIZE * 8)
        self.canvas.pack()

        self.data_history = []

    def handle_data(self, data):
        msg = data.decode()

        if msg[0] == "~":
            print("Skipped")
            return
        
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION
        matrix = data_array.reshape((8, 8))

        detected_blobs = self.blob_detection(matrix)
        total_count = sum(blob['person_count'] for blob in detected_blobs)
        print("Total count:", total_count)

        self.update_heatmap(matrix)

        self.data_history.append({
            'matrix': matrix,
            'blobs': detected_blobs
        })

    def update_heatmap(self, matrix):
        self.canvas.delete("all")

        for x in range(8):
            for y in range(8):
                intensity = int(((30 - matrix[x, y]) / 30) * 255)
                intensity = max(0, min(intensity, 255))
                color = "#{:02X}{:02X}{:02X}".format(intensity, intensity, intensity)
                self.canvas.create_rectangle(x * PIXEL_SIZE, y * PIXEL_SIZE, (x+1) * PIXEL_SIZE, (y+1) * PIXEL_SIZE, fill=color)

    def blob_detection(self, matrix):
        THRESHOLD_TEMP = 24
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
            if pixel_count <= 2:
                person_count = 1
            elif pixel_count >=3  and pixel_count <= 4:
                person_count = 2
            elif pixel_count >= 5 and pixel_count <= 6:
                person_count = 3
            elif pixel_count >= 7 and pixel_count <= 8:
                person_count = 4

            blob_data = {'coordinates': blob, 'person_count': person_count}
            blobs[blobs.index(blob)] = blob_data

        total_count = sum(blob['person_count'] for blob in blobs)
        print("Total count:", total_count)

        return blobs

    def start(self):
        try:
            server = Server()
            asyncio.run(server.start_server(GridEyeProtocol))
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nGoodbye cruel world\n")

if __name__ == "__main__":
    protocol = GridEyeProtocol()
    protocol.start()
