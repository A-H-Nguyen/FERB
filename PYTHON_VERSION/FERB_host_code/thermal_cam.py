import socket
import numpy as np
import cv2

# Define the size of the thermal image grid (8x8 for Grid-EYE)
grid_size = (8, 8)

def map_temperature(value):
    # Map the temperature value to a grayscale intensity value
    return int((value - 20) / (40 - 20) * 255)  # Normalize the temperature to the range [0, 255]

def parse_data(data):
    # Parse the received data into a list of temperature values
    temps = []
    for i in range(0, len(data), 2):
        pixel_value = data[i] | (data[i + 1] << 8)
        temps.append(pixel_value)
    return temps

def draw_thermal_image(temps):
    # Reshape the temperature values into an 8x8 grid
    grid_temps = np.array(temps).reshape(grid_size)

    # Create a blank canvas for the thermal image
    thermal_image = np.zeros((grid_size[0] * 50, grid_size[1] * 50), dtype=np.uint8)

    # Draw squares to represent each pixel of the thermal image
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            # Calculate the intensity value based on temperature
            intensity = map_temperature(grid_temps[i, j])
            # Fill the corresponding square with the calculated intensity
            thermal_image[i * 50:(i + 1) * 50, j * 50:(j + 1) * 50] = intensity

    # Display the thermal image
    cv2.imshow('Thermal Image', thermal_image)
    cv2.waitKey(1)  # Wait for a short time to allow the image to be displayed

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
        _HOST = socket.gethostname()
        _IP = '10.42.0.1'  # taken from ifconfig output
        _PORT = 12345

        print("Host Name =\t", _HOST)
        print("Host IP =\t", _IP)

        _socket.bind((_IP, _PORT))

        print(f"TCP server is listening on {(_IP, _PORT)}...\n")

        _socket.listen(1)
        connection, client_address = _socket.accept()
        print(f"Connection established with {client_address}")

        while True:
            try:
                # Receive data from the client
                data = connection.recv(128)  # Adjust buffer size as needed
                if not data:
                    raise Exception("Connection closed by client.")
                
                # Parse the received data into temperature values
                temps = parse_data(data)

                # Draw the thermal image
                # draw_thermal_image(temps)

            except Exception as e:
                print(f"Error: {e}")
                break

            except KeyboardInterrupt as k:
                print("Server terminated by keyboard interrupt.")
                connection.close()
                break

if __name__ == "__main__":
    main()
