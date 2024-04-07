"""
Main file for the FERB GUI
"""
import tkinter as tk

from FERB_widgets import ScrollableFrame, ThermalCam
from tkinter import ttk

# Global variables are a stain on this cursed world
curr_cam = 0


class ClientFrame(tk.Frame):
    """
    I can't put this in `FERB_widgets.py` because of the stupid fucking global
    variable. I fucking hate my life
    """
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

    def update_status(self, msg:str):
        self.person_count_data.config(text=msg)


class FERBApp(tk.Tk):
    """
    Main parent class for the FERB GUI. This is the worst thing I have ever
    written in my life. I hate it so fucking much.
    """
    def __init__(self):
        super().__init__()

        self.title('FERB GUI')
        self.attributes('-fullscreen',True)
        
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 2)
        
        self.left_frame = tk.Frame(self, width=400, height=400)
        self.right_frame = tk.Frame(self, width=400, height=400)

        self.left_frame.grid(row=0, column=0)
        self.right_frame.grid(row=0, column=1)

        self.left_frame.grid_propagate(False)
        self.right_frame.grid_propagate(False)

        self.create_cam()
        self.create_server_monitor()
        self.create_quit_btn()

    def create_quit_btn(self):
        """
        Fucking leave.
        """
        close_button = tk.Button(self.left_frame, text="Quit", command=self.destroy)
        close_button.grid(row=2, column=0, sticky="ew")

    def create_server_monitor(self):
        self.server_monitor = ScrollableFrame(self.left_frame, borderwidth=5, relief="ridge", width=380, height=150)
        self.server_monitor.grid(row=0, column=0, sticky = "nesw")
    
    def create_cam(self):
        self.cam = ThermalCam(self.right_frame, width=400, height=400)
        self.cam.grid(row=0, column=1, rowspan=2, sticky="nesw")

    def add_client(self, client_id):
        client_name = f"FERB{self.server_monitor.get_num_children()}"
        frame = ClientFrame(self.server_monitor.scrollable_frame,
                            client_id=client_id, client_name=client_name,
                            relief="sunken", borderwidth=1)
        self.server_monitor.add_frame(frame)

    def remove_client(self, client_id):
        self.server_monitor.remove_frame_by_id(client_id)

    def update_client_person_count(self, client_id, new_count):
        _client = self.server_monitor.get_frame(client_id)
        _client.update_status(str(new_count))


    def draw_image(self, data):
        self.cam.draw_bw_image(data)
