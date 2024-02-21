import network
from time import sleep

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

nets = wlan.scan()
print(f"\nAvailable networks:")
for net in nets:
    print(f"SSID: {net[0]}, RSSI: {net[3]}")
print(f"\n-------------------------------------\n")

ssid_test = "Ferbius"
password = "Ferbius69"

# while not wlan.isconnected():
#     print("Attempting to connect...")

#     wlan.connect(ssid=ssid_test, key=password)    
#     sleep(7)

wlan.connect(ssid=ssid_test, key=password)    
sleep(7)

if wlan.isconnected():
    print("Yippee!")
else:
    print("no")
# network.WLAN.
