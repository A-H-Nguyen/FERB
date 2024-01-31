# FERB Micropython Firmware
## Files
### `hotspot_host.py`
This is code to be run on a PC that is hosting the wi-fi hotspot.
It probably won't work on a Pico W.

### `pico_device.py`
This code has the Pico W connect to a wi-fi network, and attempt to connect to a socket running on said network.

### `test_device.py`
Simple script for connecting to a TCP socket. Don't try to run this on a Pico W, it won't work.

Instead, open a seperate terminal window and run this script there, while `hotspot_host.py` is running on another terminal.

### `umqttsimple.py` and `mqtt_device_pub.py`
A library and example code for using the UMQTT communication protocol. It's a little complicated, and will be completely unnecessary if we get TCP Sockets to work.
If you do want to use the UMQTT library, just import it like normal in whatever python script you're using. Then, remember to also upload the `umqttsimple.py` file
into your Pico W. This is NOT the same as running the file!
