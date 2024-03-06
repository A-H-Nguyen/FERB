import asyncio
import random

from graphics import *
from server_base import FerbProtocol, Server


class ThermalCam:
    def __init__(self) -> None:
        # Define the size of the thermal image grid (8x8 for Grid-EYE)
        # self.grid_size = (8, 8)
        self.win = GraphWin("Thermal Image", 400, 400)

    def map_temperature(self, value):
        if value < 0:
            return color_rgb(0, 0, 0)  # Black for negative temperatures
        elif value >= 50:
            return color_rgb(255, 0, 0)  # Bright red for temperatures >= 50
        else:
            # Map temperatures from 0 to 50 degrees Celsius to varying shades of red
            red_value = int(value * 255 / 50)  # Scale value to range [0, 255]
            return color_rgb(red_value, 0, 0)

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
