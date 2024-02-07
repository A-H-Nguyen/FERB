import socket

from graphics import *

# Define the size of the thermal image grid (8x8 for Grid-EYE)
grid_size = (8, 8)


def map_temperature(value):
    # Map the temperature value to a color ranging from blue to red
    if value <= 90:
        # Map temperatures <= 90 to shades of blue
        blue_value = int(value * 255 / 90)
        return color_rgb(0, 0, blue_value)
    else:
        # Map temperatures >= 100 to shades of red
        red_value = int((value - 90) * 255 / (150 - 90))
        return color_rgb(red_value, 0, 0)


def parse_data(data):
    # Parse the received data into a list of temperature values
    temps = []
    for i in range(0, len(data), 2):
        pixel_value = data[i] | (data[i + 1] << 8)
        temps.append(pixel_value)
    return temps


def draw_thermal_image(win, temps):
    # Draw squares to represent each pixel of the thermal image
    for row in range(8):
        for col in range(8):
            temp = temps[row * 8 + col]  # Get temperature value for current pixel
            color = map_temperature(temp)
            rect = Rectangle(Point(col * 50, row * 50), Point((col + 1) * 50, (row + 1) * 50))
            rect.setFill(color)
            rect.draw(win)


def main():
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    win = GraphWin("Thermal Image", 400, 400)

    while True:
        try:
            # Receive data from the client
            data = connection.recv(128)  # Adjust buffer size as needed
            if not data:
                raise Exception("Connection closed by client.")

            # Parse the received data into temperature values
            temps = parse_data(data)

            draw_thermal_image(win, temps)

            # Check if the user clicked the mouse to exit
            if win.checkMouse():
                connection.close()
                win.close()
                break

        except Exception as e:
            print(f"Error: {e}")
            break

        except KeyboardInterrupt as k:
            print("Server terminated by keyboard interrupt.")
            connection.close()
            break

    _socket.close()


if __name__ == "__main__":
    main()
