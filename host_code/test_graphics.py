#####################################
###  Testing how to use tkinter   ###
#####################################

import tkinter as tk
import os
import sys
import subprocess
import threading

from tkinter import ttk


# Width and Height of the Raspberry Pi screen
SCREEN_WIDTH = 800  # root.winfo_screenwidth()
SCREEN_HEIGHT = 400 # root.winfo_screenheight()


def test():
    print('Button clicked')

def run(target):
    threading.Thread(target=target).start()

def ping():
    print("Thread: start")

    p = subprocess.Popen("ping -c 4 stackoverflow.com".split(), stdout=subprocess.PIPE, bufsize=1, text=True)
    while p.poll() is None:
        msg = p.stdout.readline().strip() # read a line from the process output
        if msg:
            print(msg)

    print("Thread: end")


# Redirect the out stream for the terminal
class Redirect():
    def __init__(self, widget, autoscroll=True):
        self.widget = widget
        self.autoscroll = autoscroll

    def write(self, text):
        self.widget.insert('end', text)
        if self.autoscroll:
            self.widget.see("end")  # autoscroll

    def flush(self):
       pass


# Create root window of tkinter app
root = tk.Tk()
root.title('FERB GUI')

# This line forces the root window to always be on top of the stack
# root.attributes('-topmost', 1)

root.attributes('-fullscreen',True)

frame = tk.Frame(root)
frame.pack(expand=True, fill='both')

text = tk.Text(frame)
text.pack(side='left', fill='both', expand=True)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side='right', fill='y')

text['yscrollcommand'] = scrollbar.set
scrollbar['command'] = text.yview

old_stdout = sys.stdout    
sys.stdout = Redirect(text)

# This line sets the icon for the tkinter app
# root.iconbitmap('path')

# # place a label on the root window
# message = tk.Label(root, text="Hello, World!")
# message.pack()

# ttk.Button(root, text='Click Me', command=button_clicked).pack()
ttk.Button(root, text='TEST', command=test).pack()
ttk.Button(root, text='PING', command=lambda:run(ping)).pack()
ttk.Button(root, text="Quit", command=root.destroy).pack() 

root.mainloop()



#####################################
### Original Graphics Test Script ###
#####################################

# import asyncio
# import numpy as np

# from graphics import *
# from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION
# from scipy.interpolate import RegularGridInterpolator

# # Number of pixels for both original Grid-EYE output, and interpolated output
# _GRID_LEN = 8
# _INTRP_LEN = 16

# THRESHOLD_TEMP = 24  # Define a threshold temperature value to consider as part of a blob


# class ThermalCam:
#     def __init__(self, resolution=400) -> None:
#         # Define the size of the thermal image grid
#         self._RESOLUTION = resolution

#         self._black = color_rgb(0,0,0)

#         # Precompute the length of camera pixels for drawing
#         self._draw_dist = self._RESOLUTION / _INTRP_LEN

#         # Create the Rectangle objects for thermal image once
#         self.rectangles = []
#         for row in range(_INTRP_LEN):
#             tmp_array = []
#             for col in range(_INTRP_LEN):
#                 rect = Rectangle(Point(col * self._draw_dist, row * self._draw_dist), 
#                                  Point((col + 1) * self._draw_dist, (row + 1) * self._draw_dist))
#                 rect.setFill(self._black)           
#                 tmp_array.append(rect)
#             self.rectangles.append(tmp_array)

#         # Set the window with the given resolution
#         self.win = GraphWin("Thermal Image", self._RESOLUTION, self._RESOLUTION)

#     def draw_thermal_image(self, temps):
#         for row in range(_INTRP_LEN):
#             for col in range(_INTRP_LEN):
#                 rect = self.rectangles[row][col]
#                 rect.undraw()

#                 if temps[row, col] >= THRESHOLD_TEMP:
#                     rect.draw(self.win)


# class GridEyeProtocol(FerbProtocol):
#     def __init__(self):
#         self.wait_timer = None
#         self.TIME_LIMIT = 10

#         # Generate x and y coordinates for the original and interpolated Grid-EYE output
#         self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
#         self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
#         self.interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)

#         self.cam = ThermalCam()

#     def handle_data(self, data):
#         # Convert the bytearray to a numpy array of 16-bit integers (short ints)
#         data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

#         if data_array.size != 64:
#             print("skipped")
#             return

#         # Reshape the array to form an 8x8 matrix
#         matrix = data_array.reshape((_GRID_LEN, _GRID_LEN))

#         # Create a scipy interpolation function for our temperature reading
#         interp_func = RegularGridInterpolator((self.orig_coords, self.orig_coords), matrix)
#         interp_matrix = interp_func((self.interp_Y, self.interp_X))
#         norm_matrix = np.where(interp_matrix > THRESHOLD_TEMP, interp_matrix, 0)

#         # print("Temperature Matrix:")
#         # print(interp_matrix)
#         # print("\nDetected Blobs:")
#         # detected_blobs = self.blob_detection(matrix)
#         # detected_blobs = self.blob_detection(interp_matrix)
#         # for i, blob in enumerate(detected_blobs, start=1):
#         #     print(f"Blob {i}: {blob}")
#         # print("\n-----------------------------------------\n")
        
#         # self.cam.draw_thermal_image(matrix)
#         self.cam.draw_thermal_image(norm_matrix)

#     def blob_detection(self, matrix):
#         """
#         Perform blob detection on the temperature matrix.

#         Args:
#         - matrix (numpy.ndarray): An 8x8 matrix of temperature values.

#         Returns:
#         - List of tuples: Each tuple represents the coordinates (row, column) of the detected blobs.
#         """

#         blobs = []
#         visited = set()

#         # Define a function to perform depth-first search (DFS)
#         def dfs(row, col, blob):
#             if (row, col) in visited or row < 0 or col < 0 or row >= matrix.shape[0] or col >= matrix.shape[1]:
#                 return
#             if matrix[row][col] < THRESHOLD_TEMP:
#                 return
#             visited.add((row, col))
#             blob.append((row, col))
#             # Explore neighboring cells
#             dfs(row + 1, col, blob)
#             dfs(row - 1, col, blob)
#             dfs(row, col + 1, blob)
#             dfs(row, col - 1, blob)
#             # Diagonal exploration 
#             dfs(row - 1, col - 1, blob)
#             dfs(row - 1, col + 1, blob)
#             dfs(row + 1, col - 1, blob)
#             dfs(row + 1, col + 1, blob)

#         # Iterate through each cell in the matrix
#         for i in range(matrix.shape[0]):
#             for j in range(matrix.shape[1]):
#                 if matrix[i][j] >= THRESHOLD_TEMP and (i, j) not in visited:
#                     # Start a new blob
#                     blob = []
#                     dfs(i, j, blob)
#                     blobs.append(blob)

#         return blobs


# if __name__ == "__main__":
#     try:
#         server = Server()
#         asyncio.run(server.start_server(GridEyeProtocol))
        
#     except KeyboardInterrupt as k:
#         print("\nGoodbye cruel world\n")

