### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!
### DELETE THIS FILE!!!!



import numpy as np
import tkinter as tk


_GRID_LEN = 8
# _GRAYSCALE = 255
_THRESHOLD = 25


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
