import network
import usocket as socket
import uselect as select
import time
# import urequests

# HOT_SPOT_SSID = 'teriyaki'
# HOT_SPOT_PASS = '3V2GaaqQ'
# SERVER_IP     = '127.0.1.1'
# SERVER_PORT   = 12345

HOT_SPOT_SSID = 'NAME'
HOT_SPOT_PASS = 'PASSWORD'
SERVER_IP     = '192.168.4.1'
SERVER_PORT   = 80

wlan = network.WLAN(network.STA_IF)  # Use network.STA_IF for station mode
wlan.active(True)

# Use 'WPA-EAP' for WPA2 Enterprise authentication
# wlan.connect(ssid='NUwave', auth=(network.WLAN.WPA2_EAP,'ha.je','password'), key_mgmt='WPA-EAP')
# ssid = 'NUwave-guest'
# wlan.connect(ssid=ssid)

nets = wlan.scan()  # List with tuples (ssid, bssid, channel, RSSI, security, hidden)

# Print the list of nearby networks
# print("Available networks:")
# for net in nets:
#     ssid = net[0]  # Access the first element of the tuple for SSID
#     rssi = net[3]  # Access the fourth element of the tuple for RSSI
#     print("SSID: {}, RSSI: {}".format(ssid, rssi))
# print("") # print a new line

_wlan_connected = False
while not _wlan_connected:
    # nets = wlan.scan()
    # print(f"Not connected...\n",
    #       f"\n-------------------------------------\n",
    #       f"Available networks:")
    # for net in nets:
    #     # Access the 0th element of the tuple for SSID
    #     # Access the 3rd element of the tuple for RSSI
    #     print(f"SSID: {net[0]}, RSSI: {net[3]}")
    # print(f"\n-------------------------------------\n")

    print(f"Attempting to connect to {HOT_SPOT_SSID}...\n")
    wlan.connect(ssid=HOT_SPOT_SSID, key=HOT_SPOT_PASS)
    time.sleep(3)

    if wlan.isconnected():
        _wlan_connected = True

print(f"Connected to network on {HOT_SPOT_SSID}")

# addr_info = socket.getaddrinfo(HOT_SPOT_SSID, SERVER_PORT)
# print(addr_info)

_socket = socket.socket()
_socket_connected = False
while not _socket_connected:
    try:
        _socket.connect((SERVER_IP, SERVER_PORT))
        _socket_connected = True
        print(f"Connected to server at {(SERVER_IP, SERVER_PORT)}")

    except Exception as e:
        print(f"Connection failed: {e}")
        time.sleep(3)

_socket.sendall(b"Hello, world")        
time.sleep_ms(500)

data = _socket.recv(1024)
time.sleep_ms(500)

print(data)

_socket.close()













# _socket = socket.socket()

# # # _socket.connect((SERVER_IP, SERVER_PORT))

# # # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
# # try:

# _socket.connect(addr_info[0][-1])
#     # _socket.connect((SERVER_IP, SERVER_PORT))   
#     _socket.connect(SERVER_IP)   
# #         print(f"Received {data!r}")
# except:
#     print("failed to connect to server on teriyaki")
#     finally:
#         _socket.close()

# print("Done")


# while True:
#     _socket.sendall(b"Hello, world")        
#     data = _socket.recv(1024)
#     time.sleep_ms(500)
    # try:
    #     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     # socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    #     # Activate the server; this will keep running until you
    #     # interrupt the program with Ctrl-C
    #     server.serve_forever()
    # except:
    #     pass
    # finally:
    #     server.close()

