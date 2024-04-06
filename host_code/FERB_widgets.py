import numpy as np
import tkinter as tk

from tkinter import ttk


_GRID_LEN = 8
# _GRAYSCALE = 255
_THRESHOLD = 25


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

    def get_frame(self, frame_id):
        children = self.scrollable_frame.winfo_children()
        for child in children:
            if hasattr(child, 'id') and child.id == frame_id:
                return child

    def remove_frame_by_id(self, frame_id):
        child = self.get_frame(frame_id)
        child.pack_forget()
        child.destroy()


class ThermalCam(tk.Canvas):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self._draw_len = 50 # Hard code 50 pixels because I fucking give up

        self.prev_image = np.zeros((_GRID_LEN, _GRID_LEN), dtype=bool)
        self.curr_image = np.zeros((_GRID_LEN, _GRID_LEN), dtype=bool)

    def draw_bw_image(self, temps):
        """
        Draw the thermal image in black and white. Only pixels over a certain
        theshold are shown. If a pixel is hot enough, it appears as white.
        """
        # self.create_rectangle(0, 0, self.winfo_width(), self.winfo_height(), 
                            #   fill="black", outline='')
        print(self.prev_image)
        for row in range(_GRID_LEN):
            for col in range(_GRID_LEN):
                
                self.curr_image[row,col] = temps[row,col] >= _THRESHOLD

                if self.curr_image[row,col] == self.prev_image[row,col]:
                    continue
                
                self.prev_image[row,col] = self.curr_image[row,col]

                if not self.curr_image[row, col]:
                    color = "black"
                else:
                    color = "white"

                x0 = col * self._draw_len
                y0 = row * self._draw_len
                x1 = x0 + self._draw_len
                y1 = y0 + self._draw_len

                self.create_rectangle(x0, y0, x1, y1, fill=color, outline='')
