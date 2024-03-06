#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: Please provide the name of the server (i.e. server_base.py)."
    exit 1
else
    SERVER_PATH=$(pwd)/$1
    
    IP='10.42.0.1'
    PORT=11111

    echo "Running server: ${SERVER_PATH}"

    python3 $SERVER_PATH --ip $IP --port $PORT
fi
