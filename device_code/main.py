from FERBDevice import Ferb

# Constants for network and server configuration
HOST_SSID = 'JAYVHA'
HOST_PASS = 'test12345'
SERVER_IP = '10.110.85.119'  # IP address of the server, obtained from ifconfig output
SERVER_PORT = 12345      # Arbitrary port number for the server, ensure it's known and available

# Constants for Grid-EYE configuration
SDA_PIN = 16
SCL_PIN = 17
GRID_EYE_DEFAULT_ADDR = 0x69


if __name__ == "__main__":
    ferb = Ferb(HOST_SSID, HOST_PASS, SERVER_IP, SERVER_PORT,
                GRID_EYE_DEFAULT_ADDR, SDA_PIN, SCL_PIN)
    
    try:
        print("Attempt to connect to Wi-FI...")
        wifi_conn_status = ferb.connect_to_wifi()
        if wifi_conn_status != "Success":
            raise Exception(f"Could not connect to Wi-Fi network {HOST_SSID}: {wifi_conn_status}")
        else:
            print("Wi-fi success")
        
        print("Attempt to connect to socket server...")
        if not ferb.connect_to_socket():
            raise Exception(f"Could not connect to socket at {SERVER_IP}:{SERVER_PORT}")
        else:
            print("Socket success")
        
        print("Verify Grid-EYE...")
        if not ferb.search_for_i2c_device(GRID_EYE_DEFAULT_ADDR):
            raise Exception("Grid-EYE sensor not found")
        else:
            print("Grid-EYE success")

        ferb.led_high()

        while True:
            try:
                temp_bytes = ferb.read_temps()
                # ferb.print_temps(temp_bytes)
                ferb.send_temps(temp_bytes)
            
            except Exception as e:
                print(f"Error: {e}")

    except KeyboardInterrupt as k:
        print("Ok, bye")
    