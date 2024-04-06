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
        # client_incoming_queue.put(self.client_id)

        # self.gui.clients[self.client_id] = 0
        self.gui.add_client(self.client_id)

    def data_received(self, data):
        try:
            msg = data.decode()
            if msg[0] == '~':
                self.prep_calibration()
            else:
                print(f"Received data from {self.client_id}\n")
                data_array = np.frombuffer(data, dtype=np.uint16)

                # client_dict[self.client_id] = data_array[0]
        
        except Exception as e:
            self.print_timestamp(f"error: {e}")
        
        self.cancel_wait_timer()  # Cancel current wait timer
        self.start_wait_timer()  # Restart wait timer upon receiving data

    def connection_lost(self, exc):
        print(f"Connection with {self.client_id} closed\n")
        self.gui.remove_client(self.client_id)


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


class CamFrame(tk.Canvas):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.label = tk.Label(self, text="Hey")
        self.label.grid(row=0, column=0, sticky="ew")


class ServerMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asyncio Server Monitor")

        self.clients = {0:0}

        self.cam_fram = CamFrame(self)
        self.cam_fram.grid(row=1, column=1)

        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.grid(row=1,column=0)
    
    def add_client(self, client_id):
        client_name = f"FERB{self.scrollable_frame.get_num_children()}"
        frame = ClientFrame(self.scrollable_frame.scrollable_frame,
                                client_id=client_id, client_name=client_name,
                                relief="sunken", borderwidth=1)
        self.scrollable_frame.add_frame(frame)

    def remove_client(self, client_id):
        self.scrollable_frame.remove_frame_by_id(client_id)

    def run(self):
        self.mainloop()
    

class ClientWatcher:
    def __init__(self):
        pass

    def get_client(self, clients: queue.Queue):
        while True:
            if clients.empty():
                continue
            try:
                with lock:
                    print(clients.get(timeout=10))
                    print("\n-----------------------------------------\n")
            except:
                continue


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
