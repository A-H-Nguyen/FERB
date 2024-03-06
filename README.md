# FERB
Main code respository for the Northeastern University ECE Capstone group Spring 2024, working on FERB

## About FERB
Fire Emergency Rescue Beacon, or FERB for short, is a small device that tracks people's movement during a fire.
FERB is meant to be used in large buildings, where the layout and size can be a large hinderance to first responders.
The goal is to be able to implment both movement detection and person counting, which should allow first responders to
more easily locate people and keep track of them during a fire emergency.

The technology here could easily be adapted to many other scenarios such as security. By nature, a capstone project's
final product is largely proof of concept, with room to grow, given more time and money.

### Terminology:
 - `FERB` refers to each individual detector unit
 - `HOST` refers to the device that runs the local network and data server that the FERB units send data to.
 - `SERVER` the socket server that runs on the HOST

### This Repository:
There are two main directories in this repo. The `device_code/` and `host_code/`.
`device_code/` contains the FERBware (firmware) that will run on every FERB device.
`host_code/` contains the code for running the servers and handling data. More on this in the FERB network section.


## FERBmware 
The heart of every FERB is a Raspberry Pi Pico W. Micropython is the easiest way to create programs for this microcontroller,
and for the fast paced nature of capstone, the ability to rapidly prototype is very useful.

Additionally, each FERB has a sparkfun Grid-EYE module that houses a Panasonic AMG8333 chip. This chip allows us to use a
thermopile array for IR detection through the I2C communication protocol.

## FERB network
The network behind FERB is very simple. Each FERB unit (Pico W device) will connect to a single wi-fi network.
On this network, a "host" which can be anything from a desktop to a full-zised Raspberry Pi, will be running a socket server.
Each FERB device will then connect to this socket server. Once that has been completed, the fun begins.

## Running the FERB System
In order to run everything, let's reiterate some termina
