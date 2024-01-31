import network
import urequests

wlan = network.WLAN(network.STA_IF)  # Use network.STA_IF for station mode
wlan.active(True)

nets = wlan.scan()  # List with tuples (ssid, bssid, channel, RSSI, security, hidden)

# Print the list of nearby networks
print("Available networks:")
for net in nets:
    ssid = net[0]  # Access the first element of the tuple for SSID
    rssi = net[3]  # Access the fourth element of the tuple for RSSI
    print("SSID: {}, RSSI: {}".format(ssid, rssi))

# Use 'WPA-EAP' for WPA2 Enterprise authentication
# wlan.connect(ssid='NUwave', auth=(network.WLAN.WPA2_EAP, 'ha.je', 'password'), key_mgmt='WPA-EAP')
ssid = 'NUwave-guest'
wlan.connect(ssid=ssid)
ip = wlan.ifconfig()[0]

print(f'connected on {ip}')
if wlan.isconnected():
    print(r'Connected to', ssid)

