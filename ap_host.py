# import socket
import network

from machine import Pin

ssid = "Ferbius"
password = "donut_h@ck-m3pls"

ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password) 
#ap.active(False)

while not ap.active():
    ap.active(True)

#if ap.active():
 #   print("Access point active")

#print(ap.ifconfig())


