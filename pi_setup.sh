#!/bin/bash

# Create hotspot:
HOTSPOT_NAME=Ferbius
HOTSPOT_PASSWORD=ajetaFERB

sudo nmcli device wifi hotspot ssid ${HOTSPOT_NAME} password ${HOTSPOT_PASSWORD} ifname wlan0 

# Create venv
# python -m venv $(pwd)/.venv
# source .venv/bin/activate
