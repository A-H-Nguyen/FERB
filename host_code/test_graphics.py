#####################################
###  Testing how to use tkinter   ###
#####################################

import asyncio
import tkinter as tk
import numpy as np
import datetime
import sys
import threading
import queue  # For thread-safe communication between threads

from server_base import Server, FerbProtocol
from grid_eye_printer import GridEyeProtocol
from thermal_cam import ThermalCam
from tkinter import scrolledtext
from tkinter import ttk


_DEFAULT_IP = '10.42.0.1'
_DEFAULT_PORT = 11111

# Width and Height of the Raspberry Pi screen
SCREEN_WIDTH = 800  # self.winfo_screenwidth()
SCREEN_HEIGHT = 400 # self.winfo_screenheight()

data_queue = queue.Queue()
client_list = queue.Queue()
lock = threading.Lock()  # Create a lock


class GridEyeProtocol(FerbProtocol):
    def start_wait_timer(self):
        pass
    
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
        # self.transport = transport
        peername = transport.get_extra_info('peername')
        print(f"Connection from {peername}\n")
        client_list.put(peername)

    def data_received(self, data):
        message = data.decode()
        print(f"Received: {message}\n")

    def connection_lost(self, exc):
        print("Connection closed\n")


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


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


class FERBClientFrame(tk.Frame):
    def __init__(self, master, client_id, client_name, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self._id = client_id
        self.label = tk.Label(self, text=str(client_name))
        self.label.grid(row=0, column=0)

class ServerMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asyncio Server Monitor")

        self.label = tk.Label(self, text=f"Server running on {_DEFAULT_IP}:{_DEFAULT_PORT}")
        self.label.pack()
        # self.label.grid(row=0, column=0, columnspan=2)

        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.pack(expand=True, fill="both")

        # self.client_list_label = tk.Label(self, text="Connected Clients:")
        # self.client_list_label.grid(row=0, column=0)

        # self.client_list = scrolledtext.ScrolledText(self, width=40, height=10)
        # self.client_list.grid(row=0, column=1)

        # # await self.start_server()
        # # self.server = Server(lambda:GridEyeProtocool(self))
        # # threading.Thread(target=self.server.run).start()
        # threading.Thread(target=self.watch_clients, args=(client_list,)).start()

    def create_scrollable_gui(self):
        for i in range(20):
            frame = tk.Frame(self.scrollable_frame.scrollable_frame, relief="sunken", borderwidth=1)
            frame.configure(width=100, height=50)
            frame.grid_propagate(False)  # Prevents the frame from resizing to fit its contents

            label = tk.Label(frame, text=f"Frame {i}")
            label.pack(expand=True, fill="both")

            self.scrollable_frame.add_frame(frame)

    # async def start_server(self):
    #     # Get the current event loop
    #     loop = asyncio.get_running_loop()

    #     # Create a TCP server using the loop and the protocol class
    #     self.server = await loop.create_server(GridEyeProtocol,
    #                                            '10.42.0.1', 11111)
    #     print(f"Serving on {self.server.sockets[0].getsockname()}", "\n")
    #     
    #     async with self.server:
    #         await self.server.serve_forever()

    def update_clients(self, message):
        self.client_list.insert(tk.END, message)
        self.client_list.see(tk.END)

    def run(self):
        self.mainloop()
    
    def watch_clients(self, clients: queue.Queue):
        while True:
            if clients.empty():
                continue
            try:
                with lock:
                    new_client = clients.get(timeout=10)

                    print(new_client)
                    print("\n-----------------------------------------\n")

                    self.update_clients(new_client)
            except:
                print("Something bad happened")
                continue



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
    # threading.Thread(target=server.run).start()


    # app = CustomEventDemo()
    app.mainloop()
