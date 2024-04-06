import asyncio
import tkinter as tk
import numpy as np
import datetime
import sys
import threading
import queue  # For thread-safe communication between threads

from FERB_widgets import ScrollableFrame, ClientFrame
from server_base import Server, FerbProtocol
from thermal_cam import ThermalCam
from tkinter import scrolledtext
from tkinter import ttk


_DEFAULT_IP = '10.42.0.1'
_DEFAULT_PORT = 11111

# Width and Height of the Raspberry Pi screen
SCREEN_WIDTH = 800  # self.winfo_screenwidth()
SCREEN_HEIGHT = 400 # self.winfo_screenheight()

# ID of the current FERB camera

client_dict = {0:0}
client_incoming_queue = queue.Queue()
lock = threading.Lock()  # Create a lock


class GridEyeProtocol(FerbProtocol):
    def __init__(self, gui):
        super().__init__()
        self.gui = gui

    def prep_calibration(self):
        print("Get the fuck out of the way!!!!")

    def calibrate(self, data):
        print("Calibration finished.")

    def handle_data(self, data):
        try:
            print(data.decode())
        except:
            print("Fuck")

    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info('peername')
        self.client_id = peername[1]
        
        print(f"Connection from {peername}\n")

        global curr_cam 
        curr_cam = self.client_id 

        self.gui.add_client(self.client_id)

    def data_received(self, data):
        try:
            msg = data.decode()
            if msg[0] == '~':
                self.prep_calibration()
            else:
                global curr_cam
                print(f"Received data from {self.client_id}")
                if curr_cam == self.client_id:
                    data_array = np.frombuffer(data, dtype=np.uint16) * 0.25
                    temperatures = data_array.reshape((8,8))
                    print(temperatures)
                    self.gui.draw_image(temperatures)
        
        except Exception as e:
            self.print_timestamp(f"error: {e}")
        
        self.cancel_wait_timer()  # Cancel current wait timer
        self.start_wait_timer()  # Restart wait timer upon receiving data

    def connection_lost(self, exc):
        print(f"Connection with {self.client_id} closed\n")
        self.gui.remove_client(self.client_id)


class ClientFrame(tk.Frame):
    def __init__(self, container, client_id, client_name:str, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.id = client_id

        self.client_name = tk.Label(self, text=client_name)
        self.person_count_label = tk.Label(self, text="\nPerson Count:\n")
        self.person_count_data = tk.Label(self, text="PLACEHOLDER")

        self.display_btn = tk.Button(self, text="Display", command=self.dummy)

        self.client_name.grid(row=0, column=0, sticky="ew")
        self.person_count_label.grid(row=1, column=0, sticky="ew")
        self.person_count_data.grid(row=3, column=0, sticky="ew")
        self.display_btn.grid(row=0, column=1, columnspan=3, sticky="news")

    def dummy(self):
        global curr_cam
        curr_cam = self.id


class ServerMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asyncio Server Monitor")

        self.clients = {0:0}
        self.cam_id = 0 # ID of the client that is currently on camera

        self.left_frame = tk.Frame(self, width=400, height=400)
        self.right_frame = tk.Frame(self, width=400, height=400)
        self.left_frame.grid(row=0, column=0)
        self.right_frame.grid(row=0, column=1)
        self.left_frame.grid_propagate(False)
        self.right_frame.grid_propagate(False)
        
        self.scrollable_frame = ScrollableFrame(self.left_frame)
        self.cam = ThermalCam(self.right_frame, width=400, height=400)
        
        self.scrollable_frame.grid(row=0,column=0)
        self.cam.grid(row=0, column=0)
    
    def draw_image(self, data):
        self.cam.draw_bw_image(data)

    def add_client(self, client_id):
        client_name = f"FERB{self.scrollable_frame.get_num_children()}"
        frame = ClientFrame(self.scrollable_frame.scrollable_frame,
                            callback=draw_me(),
                            client_id=client_id, client_name=client_name,
                            relief="sunken", borderwidth=1)
        self.scrollable_frame.add_frame(frame)

    def remove_client(self, client_id):
        self.scrollable_frame.remove_frame_by_id(client_id)

    def run(self):
        self.mainloop()
    


def draw_me():
    print("AAAAAA")

if __name__ == "__main__":
    # # Create FERB GUI App
    # app = FERBApp()
    app = ServerMonitor()

    # # Overwrite system stdout
    # # old_stdout = sys.stdout    
    # # sys.stdout = Redirect(app.server_text)

    # # Create echo server 
    # # server = Server(protocol_class=EchoProtocol)
    # # server = Server(lambda:GridEyeProtocol(app.canvas, SCREEN_HEIGHT))
    # # server = Server(lambda:GridEyeProtocol('slkdf'))

    # # Run GUI and server
    # # threading.Thread(target=server.run).start()



    # server = Server(GridEyeProtocol)
    server = Server(lambda:GridEyeProtocol(app))
    threading.Thread(target=server.run).start()


    # app = CustomEventDemo()
    app.mainloop()
