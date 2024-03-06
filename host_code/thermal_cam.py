import asyncio
import random

from graphics import *
from server_base import FerbProtocol, Server


class ThermalCam:
    def __init__(self) -> None:
        # Define the size of the thermal image grid (8x8 for Grid-EYE)
        # self.grid_size = (8, 8)
        self.win = GraphWin("Thermal Image", 400, 400)

    def lerp_color(self, color1, color2, t):
        # Linear interpolation between two colors
        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)
        return (r, g, b)

    def map_temperature(self, value):
        # Define color gradients for different temperature ranges
        blue_color = (0, 0, 255)
        green_color = (0, 255, 0)
        yellow_color = (255, 255, 0)
        red_color = (255, 0, 0)
        
        normalize_bound = 22

        if value < normalize_bound:
            # Linear interpolation between blue and green based on temperature
            t = value / normalize_bound  # Normalize temperature to the range [0, 1]
            new_color = (self.lerp_color(blue_color, green_color, t))
        
        # elif value < normalize_bound + 20:
        #     # Linear interpolation between green and yellow based on temperature
        #     t = (40-value) / (normalize_bound + 20)
        #     new_color = self.lerp_color(green_color, yellow_color, t)
        
        elif value < normalize_bound + 3:
            # Linear interpolation between yellow and red based on temperature
            t = (normalize_bound + 3 - value) / (normalize_bound + 3)
            new_color = self.lerp_color(yellow_color, red_color, t)
        
        else:
            new_color = red_color
        
        return color_rgb(*new_color)


    # def map_temperature(self, value):
    #     val_scaled = value * 0.25

    #     red_val = int((val_scaled * 255) / 50)
        
    #     blue_val = int(255 - val_scaled)

    #     if red_val > 255:
    #         red_val = 255

    #     if blue_val < 0:
    #         blue_val = 0

    #     return color_rgb(red_val, 0, blue_val)

    def generate_data(self):
        return [random.randint(0, 30) for _ in range(64)]

    def draw_thermal_image(self, temps):
        # Draw squares to represent each pixel of the thermal image
        for row in range(8):
            for col in range(8):
                temp = temps[row * 8 + col]  # Get temperature value for current pixel
                color = self.map_temperature(temp)
                rect = Rectangle(Point(col * 50, row * 50), 
                                 Point((col + 1) * 50, (row + 1) * 50))
                rect.setFill(color)
                rect.draw(self.win)


class ThermalCamProtocol(FerbProtocol):
    def __init__(self):
        self.wait_timer = None
        self.TIME_LIMIT = 5

        self.cam = ThermalCam()

    def data_received(self, data):
        self.handle_data(data)
        
        self.cancel_wait_timer()  # Cancel current wait timer
        self.start_wait_timer()  # Restart wait timer upon receiving data

    def handle_data(self, data):
        temps = [(data[i] | (data[i + 1] << 8)) * 0.25 for i in range(0, len(data), 2)]

        self.cam.draw_thermal_image(temps)
    
    def connection_lost(self, exc):
        print(f"Connection with {self.peername} closed")
        self.cam.win.close()
        self.cancel_wait_timer()  # Cancel wait timer when connection is lost


if __name__ == "__main__":
    try:
        server = Server()
        asyncio.run(server.ferb_main(ThermalCamProtocol))
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
