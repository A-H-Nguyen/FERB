# # import json
# # import machine
# # import time

# # from amg88xx import AMG88XX        # Import the AMG88XX class
# # from ClientNethandler import NetHandler  # Import the NetHandler class

# from FERBDevice import FerbDevice


# class FerbCLI:
#     """
#     A class that implements a user interactive debugging interface on a FERB device 
#     """

#     def __init__(self, _device: FerbDevice) -> None:
#     # def __init__(self, msg_json_file: str) -> None:
#         self.device = _device
    
#     # def get_input(self, msg: str) -> str:
#     #     return input(msg)

#     # FERB Device commands:
#     def connect_to_wifi(self) -> bool:
#         return self.device.connect_to_wifi()

#     def connect_to_socket(self) -> bool:
#         return self.device.connect_to_socket()
    