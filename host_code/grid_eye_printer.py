import numpy as np

from server_base import FerbProtocol, Server, PIXEL_TEMP_CONVERSION


_GRID_LEN = 8


class GridEyeProtocol(FerbProtocol):
    def __init__(self):
        super().__init__()
        # Used for background subtraction
        self.background = np.zeros(shape=(_GRID_LEN, _GRID_LEN))
        self.cal_counter = 0
    
    def prep_calibration(self):
        self.print_timestamp(f"Calibrating sensor...")
        print("Get the fuck out of the way!!!!")
        
        self._cal = True
        self.background = np.zeros(shape=(_GRID_LEN, _GRID_LEN))

    def calibrate(self, data):
        self.background += data
        self.cal_counter += 1

        if self.cal_counter == 5:
            self.background /= self.cal_counter
            
            self.cal_counter = 0
            self._cal = False
          
            self.print_timestamp("Calibration finished.")

    def handle_data(self, data):
        # Convert the bytearray to a numpy array of 16-bit integers (short ints)
        data_array = np.frombuffer(data, dtype=np.uint16) * PIXEL_TEMP_CONVERSION

        # Reshape the array to form an 8x8 matrix
        temp_array = data_array.reshape((8, 8))
        if self._cal:
            self.calibrate(temp_array)
            return
       
        print(temp_array)
        print("\n-----------------------------------------\n")


if __name__ == "__main__":
    try:
        server = Server(protocol_class=GridEyeProtocol)
        server.run()
        
    except KeyboardInterrupt as k:
        print("\nGoodbye cruel world\n")
