from FERBHost import Ferb
from machine import Pin
from time import sleep_ms

# Constants for network and server configuration
HOST_SSID = 'teriyaki'
HOST_PASS = 'Gy9BtTDx'
SERVER_IP = '10.42.0.1'  # IP address of the server, obtained from ifconfig output
SERVER_PORT = 12345      # Arbitrary port number for the server, ensure it's known and available

led = Pin("LED", Pin.OUT)

if __name__ == "__main__":
    ferb = Ferb(HOST_PASS, HOST_PASS, SERVER_IP, SERVER_PORT)
    
    ferb.print_status()

    while True:
        try:
            led.toggle()
            sleep_ms(300)

        except KeyboardInterrupt as k:
            led.off()
            print("Goodnight")
            break