#####################################
###  Testing how to use tkinter   ###
#####################################

import tkinter as tk
import numpy as np
import datetime
import sys
import threading
import queue  # For thread-safe communication between threads

# from echo_server import EchoProtocol
# from server_base import Server
from thermal_cam import ThermalCam
# from tkinter import ttk


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

        self.bind("<<CustomEvent>>", self.handle_custom_event)

        # Queue for thread-safe communication
        self.event_queue = queue.Queue()

        # Start a separate thread to monitor the event queue
        self.event_thread = threading.Thread(target=self.event_listener)
        self.event_thread.daemon = True  # Thread will terminate when main thread ends
        self.event_thread.start()

        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 2)
        self.grid_rowconfigure(0, weight = 2)
        self.grid_rowconfigure(1, weight = 2)
        self.grid_rowconfigure(2, weight = 1)
        
        self.left_frame = tk.Frame(self, width=400, height=400)
        self.right_frame = tk.Frame(self, width=400, height=400)

        self.left_frame.grid(row=0, column=0)
        self.right_frame.grid(row=0, column=1)

        self.left_frame.grid_propagate(False)
        # self.right_frame.grid_propagate(False)

        self.create_canvas()
        self.create_terminal_log()
        self.create_person_counter()
        self.create_buttons()

        self.cam = ThermalCam(self.canvas, SCREEN_HEIGHT)
        self.cam.draw_thermal_image(np.random.randint(0, 6, size=(16, 16)))

    def event_listener(self):
        while True:
            # Block until an event is received
            event = self.event_queue.get()

            # Trigger the custom event
            self.event_generate("<<CustomEvent>>", when="tail")

    def handle_custom_event(self, event):
        self.cam.draw_thermal_image(np.random.randint(0, 6, size=(16, 16)))

    def trigger_custom_event(self):
        # Put an event into the queue to trigger the custom event
        self.event_queue.put("trigger_event")
    
    def create_buttons(self):
        # cam_button = tk.Button(self.left_frame, text="new colors", command=self.draw_thermal_image)
        # cam_button.grid(row=1, column=0, sticky="ew")

        # I'm not sure we even WANT a stupid quit button
        close_button = tk.Button(self.left_frame, text="Quit", command=self.destroy)
        close_button.grid(row=2, column=0, sticky="ew")
        
        event_button = tk.Button(self.right_frame, text="Event", command=self.trigger_custom_event)
        event_button.grid(row=2, column=1, sticky="ew")

    def create_terminal_log(self):
        server_frame = tk.Frame(self.left_frame, borderwidth=5, relief="ridge", width=380, height=150)
        self.server_text = tk.Text(server_frame)
        self.server_text.insert("1.0", "SERVER IS RUNNING")
        
        server_frame.grid(row=0, column=0) #, sticky = "nesw")
        self.server_text.grid(row=0, column=0, sticky="ns")

        server_frame.grid_propagate(False)
    
    def create_person_counter(self):
        counter_frame = tk.Frame(self.left_frame, borderwidth=5, relief="ridge", width=380, height=150)
        self.counter = tk.Text(counter_frame)
        self.counter.insert("1.0", "PLACEHOLDER")
        
        counter_frame.grid(row=1, column=0) #, sticky = "nesw")
        self.counter.grid(row=1, column=0, sticky="ns")

        counter_frame.grid_propagate(False)

    def create_canvas(self):
        self.canvas = tk.Canvas(self.right_frame, width=400, height=400)
        self.canvas.grid(row=0, column=1, rowspan=2, sticky="nesw")



def dummy():
    pass

def hey():
    print("hey")

def update_text(text_widget:tk.Text):
    text_widget.delete("1.0", "end")

    # Insert new text
    new_text = "Hello, World!"
    text_widget.insert("1.0", new_text)


if __name__ == "__main__":
    # # Create FERB GUI App
    app = FERBApp()

    # # Overwrite system stdout
    # # old_stdout = sys.stdout    
    # # sys.stdout = Redirect(app.server_text)

    # # Create echo server 
    # # server = Server(protocol_class=EchoProtocol)
    # # server = Server(lambda:GridEyeProtocol(app.canvas, SCREEN_HEIGHT))
    # # server = Server(lambda:GridEyeProtocol('slkdf'))

    # # Run GUI and server
    # # threading.Thread(target=server.run).start()


    # app = CustomEventDemo()
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

