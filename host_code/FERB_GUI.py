"""
Main file for the FERB GUI
"""
import numpy as np
import tkinter as tk
import threading
import queue  

from tkinter import ttk


class Redirect():
    """
    We use this to redirect text output from functions like `print` into
    the tkinter widget of our choosing
    """
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
        
        self.left_frame = tk.Frame(self, width=400, height=400)
        self.right_frame = tk.Frame(self, width=400, height=400)

        self.left_frame.grid(row=0, column=0)
        self.right_frame.grid(row=0, column=1)

        self.left_frame.grid_propagate(False)
        self.right_frame.grid_propagate(False)

        self.create_canvas()
        self.create_terminal_log()
        self.create_person_counter()
        self.create_buttons()

    def event_listener(self):
        while True:
            # Block until an event is received
            event = self.event_queue.get()

            # Trigger the custom event
            self.event_generate("<<CustomEvent>>", when="tail", data=event.data)

    def handle_custom_event(self, event):
        # self.counter.delete("1.0", "end")
        # print(event.data)
        try:
            # self.counter.insert("1.0", str(event.data))
            self.counter.config(text=str(event.data))
        except:
            # self.counter.insert("1.0", "Fuck.")
            self.counter.config(text="Fuck" + str(np.random.randint(0,100)))

    # def trigger_custom_event(self, data):
    #     # Put an event into the queue to trigger the custom event
    #     self.event_queue.put("trigger_event")
    
    def create_buttons(self):
        # cam_button = tk.Button(self.left_frame, text="new colors", command=self.draw_thermal_image)
        # cam_button.grid(row=1, column=0, sticky="ew")

        # I'm not sure we even WANT a stupid quit button
        close_button = tk.Button(self.left_frame, text="Quit", command=self.destroy)
        close_button.grid(row=2, column=0, sticky="ew")

    def create_terminal_log(self):
        server_frame = tk.Frame(self.left_frame, borderwidth=5, relief="ridge", width=380, height=150)
        self.server_text = tk.Text(server_frame)
        
        server_frame.grid(row=0, column=0, sticky = "nesw")
        self.server_text.grid(row=0, column=0, sticky="ns")

        server_frame.grid_propagate(False)
    
    def create_person_counter(self):
        counter_frame = tk.Frame(self.left_frame, borderwidth=5, relief="ridge", width=380, height=150)
        # self.counter = tk.Text(counter_frame)
        # self.counter.insert("1.0", "PLACEHOLDER")
        self.counter = ttk.Label(counter_frame, text="PLACEHOLDER")
        
        counter_frame.grid(row=1, column=0, sticky = "nesw")
        self.counter.grid(row=1, column=0, sticky="ns")

        counter_frame.grid_propagate(False)

    def create_canvas(self):
        self.canvas = tk.Canvas(self.right_frame, width=400, height=400)
        self.canvas.grid(row=0, column=1, rowspan=2, sticky="nesw")
