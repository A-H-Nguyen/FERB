import machine
import utime 

from amg88xx import AMG88XX
from ClientNethandler import NetHandler

# Constants for network and server configuration
HOST_SSID = 'Ferbius'
HOST_PASS = 'ajetaFERB'
SERVER_IP = '10.42.0.1'  
SERVER_PORT = 11111     

SDA_PIN = 16
SCL_PIN = 17


btn = machine.Pin(22, machine.Pin.IN)  # Push Button - Active LOW
led = machine.Pin(18, machine.Pin.OUT) # We don't use the Pico's in-built LED
# speaker = machine.PWM(machine.Pin(7))
i2c = machine.I2C(0, sda=SDA_PIN, scl=SCL_PIN, freq=400000)


# Create the NetHandler and Grid-EYE classes
net = NetHandler()
sensor = AMG88XX(i2c)

# we don't need a dedicated ADC class because it's so simple
adc_addr = 0x6e


def blink() -> None:
    """
    Blink the LED once
    """
    led.off()
    led.on()
    utime.sleep_ms(150)
    led.off()


# def blink_with_beep() -> None:
#     """
#     Blink the LED. With a beep!
#     """
#     led.off()
#     led.on()
#     # speaker.on()
#     utime.sleep_ms(150)
#     led.off()
#     # speaker.off()


def read_adc() -> int:
    """
    Get the raw ADC reading. We don't care about the actual voltage
    """
    i2c.writeto(adc_addr, b'\x00')
    adc_data = i2c.readfrom(adc_addr, 2)

    return (adc_data[0] & 0x0F) * 256 + adc_data[1]


def send_data():
    """
    Send the Grid-EYE data to the server
    """
    sensor.refresh() # Read Grid-EYE data
    utime.sleep_ms(100)
    net.send_to_socket(sensor.get_buf())
    utime.sleep_ms(100)


def calibrate():
    """
    Start the FERB calibration sequence
    """
    net.send_to_socket(bytearray("~", "utf-8"))
    led.on()
    utime.sleep(8)

    counter = 0
    while counter < 5:
        send_data()
        blink()
        utime.sleep_ms(200)

        counter += 1
        print(f"Calibration step {counter}")

    print("Cal finished")
    utime.sleep(3)


def on_boot():
    """
    Boot sequence for the FERB Device.
    
    Connects to the local network and the TCP server on the FERB-deck.

    Returns:
        bool: True if all connections are successful, False otherwise.
    """
    blink()
    if not net.is_wifi_connected():
        print(f"Attempting to connect to {HOST_SSID} ...")
        while not net.is_wifi_connected():
            net.connect_to_wifi(HOST_SSID, HOST_PASS)
            utime.sleep(5)
            blink()

    print(f"Successfully connected to {net.get_ssid()}\n")
    print(f"Attempting to connect to socket {SERVER_IP}:{SERVER_PORT} ...")
    
    try:
        net.connect_to_socket(SERVER_IP, SERVER_PORT)
        print(f"Socket connection successful\n")

        calibrate()

    except Exception as e:
        print(f"Damn.")
        panic(e)
  
    return True


def FERB_main():
    """
    Main program for the FERB device. 
    
    If the FERB is properly connected to the local network and server, it will 
    wait for the ADC to output a high value. This high value means that the
    microphone is detecting a fire alaram signal. When this occurs, the FERB
    will begin continuously sending sensor data.
    """
    while True:
        try:
            if btn.value() == 0:
                calibrate()

            reading = read_adc()
            print(reading)
            
            # if reading < 9: 
            #     net.send_to_socket(bytearray("!", "utf-8"))
            #     blink()
            #     utime.sleep(8)
            #     continue

            send_data()
            blink()

        # Spaz out if something bad happens
        except Exception as e:
            panic(e)

        except KeyboardInterrupt as k:
            net.disconnect_socket()
            utime.sleep_ms(200)

            led.off()
            
            print("Ok, bye")

            break


def panic(e):
    while True:
        print(f"Error: {e}")
        blink()
        utime.sleep_ms(200)
        blink()
        utime.sleep_ms(200)
        blink()
        utime.sleep_ms(600)


if __name__ == "__main__":
    i2c.writeto(adc_addr, b'\x10')
    
    if on_boot(): 
        FERB_main()
