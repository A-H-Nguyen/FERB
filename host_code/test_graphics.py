import asyncio
import tkinter as tk
import numpy as np
import datetime
import sys
import threading
import queue  # For thread-safe communication between threads

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

    def get_num_children(self) -> int:
        return len(self.scrollable_frame.grid_slaves())
    
    def add_frame(self, frame):
        frame_num = self.get_num_children() + 1
        frame.grid(row= frame_num, column=0, sticky="ew")

        print(f"Added frame number {frame_num}")

    def remove_frame_by_id(self, frame_id):
        children = self.scrollable_frame.winfo_children()
        for child in children:
            if hasattr(child, 'id') and child.id == frame_id:
                child.pack_forget()
                child.destroy()
                break


class FERBClientFrame(tk.Frame):
    def __init__(self, container, client_id, client_name:str, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.id = client_id
        self.client_name = tk.Label(self, text=client_name)
        self.data = tk.Label(self, text="Placeholder")

        self.client_name.grid(row=0, column=0, sticky="ew")
        self.data.grid(row=1, column=0, sticky="ew")


class CamFrame(tk.Canvas):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.label = tk.Label(self, text="Hey")
        self.label.grid(row=0, column=0, sticky="ew")

class ServerMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asyncio Server Monitor")

        # self.label = tk.Label(self, text=f"Server running on {_DEFAULT_IP}:{_DEFAULT_PORT}")
        # self.label.pack()
        # self.label.grid(row=0, column=0)

        self.clients = {0:0}

        self.create_scrollable_gui()
        self.cam_fram = CamFrame(self)
        self.cam_fram.grid(row=1, column=1)

        # self.client_incoming_queue_label = tk.Label(self, text="Connected Clients:")
        # self.client_incoming_queue_label.grid(row=0, column=0)

        # self.client_incoming_queue = scrolledtext.ScrolledText(self, width=40, height=10)
        # self.client_incoming_queue.grid(row=0, column=1)

        # # await self.start_server()
        # # self.server = Server(lambda:GridEyeProtocool(self))
        # # threading.Thread(target=self.server.run).start()
        
        # threading.Thread(target=self.watch_clients, args=(client_incoming_queue,)).start()

    def create_scrollable_gui(self):
        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.grid(row=1,column=0)
        # for i in range(20):
        #     frame = FERBClientFrame(self.scrollable_frame.scrollable_frame, 
        #                             client_id=i, client_name=f"FERB{i}",
        #                              relief="sunken", borderwidth=1)
        #     frame.configure(width=100, height=50)
        #     frame.grid_propagate(False)  # Prevents the frame from resizing to fit its contents
        #     label = tk.Label(frame, text=f"Frame {i}")
        #     label.pack(expand=True, fill="both")
            # self.scrollable_frame.add_frame(frame)

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

    def add_client(self, client_id):
        # self.client_incoming_queue.insert(tk.END, message)
        # self.client_incoming_queue.see(tk.END)
        client_name = f"FERB{self.scrollable_frame.get_num_children()}"
        frame = FERBClientFrame(self.scrollable_frame.scrollable_frame,
                                client_id=client_id, client_name=client_name,
                                relief="sunken", borderwidth=1)
        self.scrollable_frame.add_frame(frame)

    def remove_client(self, client_id):
        self.scrollable_frame.remove_frame_by_id(client_id)

    def run(self):
        self.mainloop()
    
    # def watch_clients(self, clients: queue.Queue):
    #     print("The watcher has arrived")
    #     while True:
    #         if clients.empty():
    #             continue
    #         try:
    #             with lock:
    #                 print("New client detected")
    #                 new_client = clients.get(timeout=10)
    #                 self.add_client(new_client)

    #         except Exception as e:
    #             print(f"Error: {e}")
    #             continue



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
    server = Server(lambda:GridEyeProtocol(app))
    threading.Thread(target=server.run).start()


    # app = CustomEventDemo()
    app.mainloop()
