# FERB
Main code respository for the Northeastern University ECE Capstone group Spring 2024, working on FERB

## About FERB
Fire Emergency Rescue Beacon, or FERB for short, is a system of small devices that track people's movement during emergencies.
FERB is meant to be used in large buildings, where the layout and size can be a large hinderance to first responders.
The goal is to be able to implment both movement detection and person counting, which should allow first responders to
more easily locate people and keep track of them during a fire emergency.

The technology here could easily be adapted to many other scenarios such as security. By nature, a capstone project's
final product is largely proof of concept, with room to grow, given more time and money.

### Terminology:
 - FERB: each individual detector unit
 - HOST: the device that runs the local network and data server that the FERB units send data to
 - SERVER: the socket server that runs on the HOST
 - [Micropython](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html):
   An implementation of Python 3 that is designed to be run on embedded hardware

### This Repository:
There are two main directories in this repo. The `device_code/` and `host_code/`.

These should be self explanatory. I'll explain it anyways.
`device_code/` contains the FERBware (firmware) that will run on every FERB device.
`host_code/` contains the code for running the servers and handling data.


## FERBware 
The heart of every FERB is a Raspberry Pi Pico W. Micropython is the easiest way to create programs for this microcontroller,
and for the fast paced nature of capstone, the ability to rapidly prototype is very useful.

Each FERB is also equipped with a Sparkfun Grid-EYE module that houses a Panasonic AMG8333 chip. This chip allows us to use a
thermopile array for IR detection through the I2C communication protocol. Again, the code that controls the Grid-EYE
is found within `device_code/`.

One important note to make is that the FERB units do next to nothing in terms of data processing (or at least, they are
intended not to). This is because though the Raspberyy Pi Pico is a relatively powerful microprocessor, especially when compared
to others in its weight class like the Arduino Nano, the performance overhead of using Python, and the large amount of data
means that we're going to be pushing the Pico's RP2040 chip quite a lot. We also have to account for power consumption and
overheads from network communication. Overall, this means that the simpler the FERBware is, the better.


## FERB network
The network behind FERB is very simple. Each FERB unit (Pico W device) will connect to a single wi-fi network.
On this network, a "host" which can be anything from a desktop to a full-zised Raspberry Pi, will be running a socket server.
Each FERB device will then connect to this socket server.

The current FERBware is set so that each FERB automatically connects to the wi-fi network and the socket server on boot.
**This means that before turning on any FERBs, we want to make sure that the Host's wi-fi and socket server are running.**
This should theoretically be accounted for by calling `machine.reset()` when the FERBware main script encounters an error.
However, this has not been widely tested, and constantly resetting the Pico might create problems.

Within the `host_code/` directory, you'll find a few things. First, is another README! 
This contains all the directions on how to run the various servers, as well as descriptions on what the servers do.
Additionally, there are some shell scripts. Hopefully their names are self explanatory, but there will be more detailed
descriptions in the host code README. Lastly, there is the fun stuff. 

We are using asyncio servers for the host because it is able to handle multiple connections very easily.
Every server imports the `server_base.py` module. In this module, there are 3 classes, `CLI`, `FerbProtocol`, and `Server`.
The protocol class is required by the asyncio to define methods for handling connections, sending/receiving data, etc.
In every server, we create a new protocol that inherits from `FerbProtocol`, and that overrides the `handle_data()` method.
They should all follow the same overall structure, which should allow us to create many different testing/demo servers as needed.


## FERB Setup
There are two parts to this: setting up the FERB devices, and setting up the Host.

### Host Setup
The Host is the simpler of these two. Just clone this repository on your Host device, and then follow the directions in
`host_code/` for the server that you want to run.

### Device Setup
For the FERB device, we need to flash the Raspberry Pi Pico W. The first step of this is making sure that the Micropython
bootloader is on the Pico. You can download the latest version [here](https://micropython.org/download/RPI_PICO_W/).
To flash the Pico, make sure it's unplugged, hold down the BOOTSEL button (there's only ONE button on the Pico, and it is this
button) and then plug the Pico into your computer via USB. The Pico should open up as if its a USB thumbdrive. Then, just drag
and drop the Micropython UF2 into the Pico. It should reset on its own.

Next, we have to save the files from `device_code/` into the Raspberry Pi Pico. There are a few ways to do this.
My personal favorite is using the micropico extension on VSCode, but you can also use the Thonny IDE. The latter is convenient
because Thonny is installed by default on the Raspbian OS, however I think VSCode is better. More on flashing the Pico in the next section.

Once the Pico is flashed, we also have to verify that the Grid-EYE is plugged in properly. The FERB PCB should already account for this, however, this information is important if you want to make o FERB on a breadboard.
We are using the i2c0 bus on the Pico,with GPIO 16 and 17 for SDA and SCL respectively. Furthermore, the Grid-EYE specifies 3.3V power, which means that we want to power it with the Pico's 3V3(OUT) Pin, and *not* the 5V VSYS Pin. 

### Flashing with the MicroPico Extension
Open `device_code/` in a new VSCode window (you can press `Ctrl + shift + N` or go to File->New Window).
Then press `Ctrl + shift + P`. This will bring up VSCode's command window. Feel free to type "MicroPico" in order to browse all
of the extension's lovely commands.

For now, we only need two.

First, run `MicroPico: Configure Project`. This should generate a `.micropico` file inside your device code directory.
Along with that, you should see a new toolbar at the bottom of the screen. With this toolbar, make sure that in the bottom left
check mark next to "Pico Connected". Otherwise your Pico is... not connected... yeah. And that's a bad thing.

Once your Pico is connected, run `MicroPico: Upload project to Pico`. After a few seconds... we should be done!
Now you can either run `main.py` manually from VSCode using the button on the bottom toolbar, or you can unplug the Pico from
USB, and power the Pico using an external supply. The `main.py`script will automatically run when the Pico powers on. This is
where we want to make sure the server is running before trying to run the FERB unit, as the second we power it on, it will try to connect.

## Running the FERB System
Once setup is complete, running FERB should be easy :)

First, run the host server.

Then, turn on your FERBs! (Or you can run `main.py` from VSCode or Thonny)

You should see the results from the server automatically. If you don't... then that's where the "engineering" part comes in...
