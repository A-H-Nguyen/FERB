#!/bin/bash

# Create hotspot:
HOTSPOT_NAME=Ferbius
HOTSPOT_PASSWORD=ajetaFERB

sudo nmcli device wifi hotspot ssid ${HOTSPOT_NAME} password ${HOTSPOT_PASSWORD} ifname wlan0 
