"""
Main file for the FERB GUI
"""
import sys
import threading
import tkinter as tk

from server_base import Server
from thermal_cam import GridEyeProtocol


# Width and Height of the Raspberry Pi screen
SCREEN_WIDTH = 800  # self.winfo_screenwidth()
SCREEN_HEIGHT = 400 # self.winfo_screenheight()


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
        self.create_buttons()

    def create_buttons(self):
        # cam_button = tk.Button(self.left_frame, text="new colors", command=self.draw_thermal_image)
        # cam_button.grid(row=1, column=0, sticky="ew")

        # I'm not sure we even WANT a stupid quit button
        close_button = tk.Button(self.left_frame, text="Quit", command=self.destroy)
        close_button.grid(row=1, column=1, sticky="ew")

    def create_canvas(self):
        server_frame = tk.Frame(self.left_frame, borderwidth=5, relief="ridge", width=380, height=250)
        self.server_text = tk.Text(server_frame)
        
        server_frame.grid(row=0, column=0, columnspan=2) #, sticky = "nesw")
        self.server_text.grid(row=0, column=0, sticky="ns")

        server_frame.grid_propagate(False)

    def create_terminal_log(self):
        self.canvas = tk.Canvas(self.right_frame, width=400, height=400)
        self.canvas.grid(row=0, column=2, rowspan=2, sticky="nesw")


if __name__ == "__main__":
    # Create FERB GUI App
    app = FERBApp()

    # Overwrite system stdout
    # A whole section of this GUI relies in this. I hate it.
    old_stdout = sys.stdout    
    sys.stdout = Redirect(app.server_text)

    server = Server(lambda:GridEyeProtocol(app.canvas, SCREEN_HEIGHT))

    # Run GUI and server
    threading.Thread(target=server.run).start()
    app.mainloop()
