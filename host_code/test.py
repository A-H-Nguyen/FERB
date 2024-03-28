import asyncio
import numpy as np

# from graphics import *
from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION
from scipy.interpolate import RegularGridInterpolator

# from kivy.app import App
# # from kivy.clock import Clock
# from kivy.config import Config
# # from kivy.graphics import Mesh, Color
# # from kivy.graphics.texture import Texture
# # from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.widget import Widget


# # SCREEN_LEN = 800
# # RESOLUTION = 8
# # PIXEL_LEN = int(SCREEN_LEN / RESOLUTION)


# # # Set the window size
# # Config.set('graphics', 'width', str(SCREEN_LEN))
# # Config.set('graphics', 'height', str(SCREEN_LEN))


# # class ThermalCameraWidget(Widget):
# #     def __init__(self, **kwargs):
# #         super().__init__(**kwargs)

# #         self.colors = np.zeros((RESOLUTION, RESOLUTION, 3), dtype=np.uint8)

# #         self.texture = Texture.create(size=(RESOLUTION,RESOLUTION), colorfmt="rgb")
# #         self.texture.blit_buffer(self.colors.tobytes(), colorfmt='rgb', bufferfmt='ubyte')

# #         self.mesh = self.build_mesh()
# #         self.mesh.texture = self.texture
# #         self.canvas.add(self.mesh)

# #     def build_mesh(self):
# #         vertices = []
# #         indices = []
# #         # for row in range(RESOLUTION):
# #         #     for col in range(RESOLUTION):
# #         #         x = col * PIXEL_LEN
# #         #         y = row * PIXEL_LEN
# #         #         vertices.extend([x, y, 0, 
# #         #                          x + PIXEL_LEN, y, 0, 
# #         #                          x, y + PIXEL_LEN, 0, 
# #         #                          x + PIXEL_LEN, y + PIXEL_LEN, 0])
# #         #         indices.extend([4 * (row * RESOLUTION + col), 
# #         #                         4 * (row * RESOLUTION + col) + 1, 
# #         #                         4 * (row * RESOLUTION + col) + 2, 
# #         #                         4 * (row * RESOLUTION + col) + 3])

# #         # for row in range(RESOLUTION + 1):
# #         #     for col in range(RESOLUTION + 1):
# #         #         x = col * PIXEL_LEN
# #         #         y = row * PIXEL_LEN
# #         #         vertices.extend([x, y, 0])
    
# #         # for row in range(RESOLUTION):
# #         #     for col in range(RESOLUTION):
# #         #         indices.extend([row * (RESOLUTION + 1) + col,
# #         #                        (row + 1) * (RESOLUTION + 1) + col,
# #         #                        (row + 1) * (RESOLUTION + 1) + col + 1,
# #         #                         row * (RESOLUTION + 1) + col + 1])



# #         return Mesh(vertices=vertices, indices=indices, mode='lines')

# #     def on_touch_down(self, touch):
# #         self.colors[:, :] = np.random.randint(0, 255, size=(RESOLUTION, RESOLUTION, 3), dtype=np.uint8)
# #         self.texture.blit_buffer(self.colors.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
# #         self.mesh.texture = self.texture


# # class ThermalCameraApp(App):
# #     def build(self):
# #         return ThermalCameraWidget()
# #         # wid = Widget()
# #         # with wid.canvas:
# #         #     self.mesh = self.build_mesh()
        
# #         # layout = BoxLayout(size_hint=(1, None), height=50)

# #         # root = BoxLayout(orientation='vertical')
# #         # root.add_widget(wid)
# #         # root.add_widget(layout)


# # if __name__ == '__main__':
# #     ThermalCameraApp().run()

# # #     #     with self.canvas:
# # #     #         # Rectangle(texture=self.create_texture((77, 255, 195)),
# # #     #         #           pos=touch.pos, size=(PIXEL_LEN, PIXEL_LEN))
# # #     #         for i in self.rect_dict.keys():
# # #     #             for rect in self.rect_dict[i]:
# # #     #                 rect.texture = self.create_texture(tuple(np.random.randint(0, 255, size=3)))


# # #     # Create a solid color texture (RGB format)
# # #     # def create_texture(self, color: tuple[int, int, int] = (0,0,0)):
# # #     # def create_texture(self):
# # #     #     # color_array = np.full((PIXEL_LEN, PIXEL_LEN, 3), color, dtype=np.uint8)

# # #     #     texture = Texture.create(size=(PIXEL_LEN,PIXEL_LEN), colorfmt="rgb")
# # #     #     # texture.blit_buffer(color_array.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
# # #     #     texture.blit_buffer(self.colors.tobytes(), colorfmt='rgb', bufferfmt='ubyte')

# # #     #     return texture
# # from kivy.app import App
# # from kivy.uix.gridlayout import GridLayout
# # from kivy.uix.boxlayout import BoxLayout
# # from kivy.uix.widget import Widget
# # from kivy.graphics import Color, Rectangle
# # from random import random

# class ColorGridWidget(Widget):
#     def __init__(self, resolution, **kwargs):
#         super().__init__(**kwargs)
#         self.resolution = resolution
# #         self.texture = Texture.create(size=(RESOLUTION,RESOLUTION), colorfmt="rgb")
# #         self.texture.blit_buffer(self.colors.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
# #         self.build_grid()

# #     def build_grid(self):
# #         grid_layout = GridLayout(cols=self.resolution, spacing=5)
# #         cell_size = (self.width / self.resolution, self.height / self.resolution)
# #         for _ in range(self.resolution):
# #             for _ in range(self.resolution):
# #                 color = (random(), random(), random(), 1)  # Random RGBA color
# #                 cell = Widget(size=cell_size)
# #                 with cell.canvas:
# #                     Color(*color)
# #                     Rectangle(pos=cell.pos, size=cell.size)
# #                 grid_layout.add_widget(cell)
# #         self.add_widget(grid_layout)

# #     def on_size(self, instance, value):
# #         self.clear_widgets()
# #         self.build_grid()

# class ColorGridApp(App):
#     def build(self):
#         return ColorGridWidget(resoultion=4)

# if __name__ == '__main__':

#     ColorGridApp().run()

# Number of pixels for both original Grid-EYE output, and interpolated output
_GRID_LEN = 8
_INTRP_LEN = 16
_GRAYSCALE = 255


class GridEyeProtocol(FerbProtocol):
    def __init__(self):
        super().__init__()
        
        # Generate x and y coordinates for the original and interpolated Grid-EYE output
        self.orig_coords = np.linspace(0, _GRID_LEN-1, _GRID_LEN)
        self.new_coords = np.linspace(0, _GRID_LEN-1, _INTRP_LEN)
        self.interp_X, self.interp_Y = np.meshgrid(self.new_coords, self.new_coords)

        # Used for background subtraction
        self.background = np.zeros(shape=(_INTRP_LEN, _INTRP_LEN))
        
        # Variables for calibration sequence
        self.cal_finished = True
        self.cal_counter = 1

        # Default values for range of temps post-background subtraction
        self.min_val = 0
        self.max_val = 5

    def calibrate(self, input_matrix) -> None:
        self.background += input_matrix
        self.cal_counter += 1

        if self.cal_counter > 5:
            self.background /= self.cal_counter
            self.cal_finished = True
            print("\nCalibrating done.")
            print("\n-----------------------------------------\n")

    def convert_to_grayscale(self, value) -> int:
        return int(((value - self.min_val) / (self.max_val - self.min_val)) * _GRAYSCALE)

    def normalize_data(self, data):
        for row in range(_INTRP_LEN):
            for col in range(_INTRP_LEN):
                if data[row,col] < self.min_val:
                    self.min_val = data[row,col]
                if data[row,col] > self.max_val:
                    self.max_val = data[row,col]

        print("Min val:", self.min_val,
              "Max val:", self.max_val)

        for row in range(_INTRP_LEN):
            for col in range(_INTRP_LEN):
                data[row,col] = self.convert_to_grayscale(data[row,col])

        print(data)

    def handle_data(self, data):
        msg = data.decode()
        if msg[0] == '~':
            # start calibration sequence here
            print("\nCalibrating sensor. Get out of the way\n")
            self.cal_finished = False
            return

        # Convert the bytearray to a numpy array of 16-bit integers (short ints)
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

        if data_array.size != 64:
            print("skipped")
            return

        # Convert the bytearray to a numpy array of 16-bit integers (short ints)
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

        # Reshape the array to form an 8x8 matrix
        matrix = data_array.reshape((8, 8))

        # Create a scipy interpolation function for our temperature reading
        interp_func = RegularGridInterpolator((self.orig_coords, self.orig_coords), matrix)
        interp_matrix = interp_func((self.interp_Y, self.interp_X))
        
        if not self.cal_finished:
            self.calibrate(interp_matrix)
            return
        
        # diff_matrix = np.round(interp_matrix - self.background) 
        # print(diff_matrix)
        # self.normalize_data(diff_matrix)
        # for row in range(_INTRP_LEN):
        #     for col in range(_INTRP_LEN):
        #         print(diff_matrix[row,col], end='  ')
        #     print('\n')
        print("\n-----------------------------------------\n")


if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.start_server(GridEyeProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
