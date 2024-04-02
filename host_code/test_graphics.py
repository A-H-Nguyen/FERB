#####################################
###  Testing how to use tkinter   ###
#####################################

import tkinter as tk
import datetime
import sys
import subprocess
import threading
import random

from echo_server import EchoProtocol
from server_base import Server
from tkinter import ttk


# Width and Height of the Raspberry Pi screen
SCREEN_WIDTH = 800  # self.winfo_screenwidth()
SCREEN_HEIGHT = 400 # self.winfo_screenheight()


# Redirect text outputs from the terminal
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


class FERBApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('FERB GUI')
        self.attributes('-fullscreen',True)

        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 2)
        
        left_frame = tk.Frame(self, width=400, height=400)
        server_frame = tk.Frame(left_frame, borderwidth=5, relief="ridge", width=395, height=250)
        self.server_text = tk.Text(server_frame)
        
        cam_button = tk.Button(left_frame, text="new colors", command=self.draw_thermal_image)
        close_button = tk.Button(left_frame, text="Quit", command=self.destroy)

        right_frame = tk.Frame(self, width=400, height=400)
        self.canvas = tk.Canvas(right_frame, width=400, height=400)

        left_frame.grid(row=0, column=0)
        server_frame.grid(row=0, column=0, columnspan=2, sticky = "nesw")
        self.server_text.grid(row=0, column=0, sticky="ns")

        cam_button.grid(row=1, column=0, sticky="ew")
        close_button.grid(row=1, column=1, sticky="ew")

        right_frame.grid(row=0, column=1)
        self.canvas.grid(row=0, column=2, rowspan=2, sticky="nesw")

        left_frame.grid_propagate(False)
        server_frame.grid_propagate(False)
        right_frame.grid_propagate(False)

    def draw_thermal_image(self):
        print(f"{datetime.datetime.now()}: new colors!")
        for row in range(16):
            for col in range(16):
                temp = random.randint(1,3)
                if temp == 1:
                    color = "blue"
                elif temp == 2:
                    color = "green"
                else:
                    color = "yellow"
                x0 = col * 24
                y0 = row * 24
                x1 =  x0 + 24
                y1 =  y0 + 24
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='')


if __name__ == "__main__":
    # Create FERB GUI App
    app = FERBApp()

    # Overwrite system stdout
    old_stdout = sys.stdout    
    sys.stdout = Redirect(app.server_text)

    # Create echo server 
    server = Server(protocol_class=EchoProtocol)

    # Run GUI and server
    threading.Thread(target=server.run).start()
    app.mainloop()




# if __name__ == "__main__":
    # Create echo server 
    # server = Server(protocol_class=EchoProtocol)

    # # Create self window of tkinter app
    # self = tk.Tk()
    # self.title('FERB GUI')
    # self.geometry("800x400")

    # self.attributes('-fullscreen',True)

    # self.grid_columnconfigure(0, weight = 1)
    # self.grid_columnconfigure(1, weight = 1)
    # self.grid_rowconfigure(0, weight = 1)

    # calc = tk.Frame(self, bg = "red")
    # calc.grid(row = 0, column = 0, sticky = "nesw")
    # history = tk.Frame(self, bg = "blue")
    # history.grid(row = 0, column = 1, sticky = "nesw")

    # # close button
    # close_button = ttk.Button(self, text="Quit", command=self.destroy)
    # close_button.grid(column=0, row=0, sticky=tk.EW)


    # frame = tk.Frame(self)
    # frame.pack(expand=True, fill='both')

    # text = tk.Text(frame)
    # text.pack(side='left', fill='both', expand=True)

    # scrollbar = tk.Scrollbar(frame)
    # scrollbar.pack(side='right', fill='y')

    # text['yscrollcommand'] = scrollbar.set
    # scrollbar['command'] = text.yview

    # old_stdout = sys.stdout    
    # sys.stdout = Redirect(text)

    # # This line sets the icon for the tkinter app
    # # self.iconbitmap('path')

    # # place a label on the self window
    # message = tk.Label(self, text="Hello, World!")
    # message.pack()

    # ttk.Button(self, text='Click Me', command=button_clicked).pack()
    # ttk.Button(self, text='RUN SERVER', command=lambda:run(server.run)).pack()
    # ttk.Button(self, text='STOP SERVER', command=server.stop).pack()
    
    # ttk.Button(self, text="Quit", command=self.destroy).pack() 

    # Run server and GUI
    # threading.Thread(target=server.run).start()
    # self.mainloop()



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

