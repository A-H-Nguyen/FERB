# FERB
Main code respository for the Northeastern University ECE Capstone group Spring 2024, working on FERB

## About FERB
Fire Emergency Rescue Beacon, or FERB for short, is a small device that tracks people's movement during a fire.
FERB is meant to be used in large buildings, where the layout and size can be a large hinderance to first responders.
The goal is to be able to implment both movement detection and person counting, which should allow first responders to
more easily locate people and keep track of them during a fire emergency.

The technology here could easily be adapted to many other scenarios such as security. By nature, a capstone project's
final product is largely proof of concept, with room to grow, given more time and money.

### The FERB network
The network behind FERB is very simple. Each FERB unit (Pico W device) will connect to a single wi-fi network.
On this network, a "host" which can be anything from a desktop to a full-zised Raspberry Pi, will be running a socket server.
Each FERB device will then connect to this socket server. Once that has been completed, the fun begins.

#### Raspberry Pi Host:
You want to use a full-sized Raspberry Pi as a host? Fine.

The following was done on a Raspberry Pi 3 Model B+ because we're not made of money. If you have like, updated hardware
or something then your results might vary. Simply install the Raspbian Desktop of your choosing, and use the `nmcli`.
You might need to run some `systemctl` commands to start the network manager.

Once the network manager is working properly, you can use the `pi_setup.sh` script, or just run the following commands:
```Bash
# Run hotspot:
sudo nmcli device wifi hotspot ssid ${HOTSPOT_NAME} password ${HOTSPOT_PASSWORD} ifname wlan0 

# Show the Wi-Fi name and password:
nmcli dev wifi show-password

# Kill hotspot:
nmcli device disconnect wlan0

```

### FERB Firmware 
The heart of the FERB is a Raspberry Pi Pico W. Micropython is the easiest way to create programs for this microcontroller,
and for the fast paced nature of capstone, the ability to rapidly prototype is very useful.

This repository is split into a few main directories. The **FERBware** (firmware) in `device_code/` and the `*_host_code/`.
The latter of which takes care of running the servers and handling data, as described in the FERB Network section.

## Running the FERBware
Maybe I'll write this later
