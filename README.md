# FERB
Main code respository for the Northeastern University ECE Capstone group Spring 2024, working on FERB

## About FERB
Fire Emergency Rescue Beacon, or FERB for short, is a small device that tracks people's movement during a fire.
FERB is meant to be used in large buildings, where the layout and size can be a large hinderance to first responders.
The goal is to be able to implment both movement detection and person counting, which should allow first responders to
more easily locate people and keep track of them during a fire emergency.

The technology here could easily be adapted to many other scenarios such as security. By nature, a capstone project's
final product is largely proof of concept, with room to grow, given more time and money.

### FERB Firmware... FERBware
The heart of the FERB is a Raspberry Pi Pico W. Micropython is the easiest way to create programs for this microcontroller,
and for the fast paced nature of capstone, the ability to rapidly prototype is very useful.

This repository is split into 2 main directories. The **FERBware** (firmware) in `device_code/` and the `host_code/` which
takes care of running the servers and handling data.

### The FERB network
I'm not writing this, I'm tired.

## Running the FERBware
Do we need details here? We're probably the only ones who'll ever read this.

I don't feel like writing anything else, DM me if you have issues.
