# FERB Host Code

## Hotspot
Before we can run any of the servers, we need a hotspot for the FERBs to connect to.
This can either be done through the desktop UI of whatever host system being used, or through the terminal.

For the Raspberry Pi Host, the `nmcli` tool is used to manage networks such as the Hotspot.
The `run_hotspot.sh` shell script uses nmcli to create a wi-fi hotspot on device wlan0. If you have multiple
wi-fi capable devices on a Host machine, you need to check which one(s) are able to use AP mode. If you cannot
use AP mode, you can't run a hotspot. Plain and simple.


## Running a Server
Servers should be run using the `run_server.sh` script. The script assumes that a server is named in order to be run:
```Bash
./run_server.sh <server_name>.py
```

The reason for the shell script is to esnure the supplied ip and port are consistent without having to copy them
into the command line for every server.

By default, these values are set for our Raspberry Pi Host:
```Bash
IP='10.42.0.1'
PORT=11111
```
So change them as needed. HOWEVER! If you change these values here, you will need to update the FERBware to match.

### Virtual Environment
Some of the servers will require Python packages that are not part of the defaul library.
Installing Python packages can be a huge hassle, even with `pip`, however creating a virtual environment makes this
much, MUCH easier.

```Bash
# Create a virtual environment if one does not already exist in this directory
python3 -m venv ferb_env

# Activate the virtual environment
source ferb_env/bin/activate

# Install the required packages
pip install -r requirements.txt

# Call this when you are done to leave the virtual environment
deactivate
```

The virtual environment ensures that packages installed with pip will be detected by the interpreter.
Futhermore, it ensures that we only have the required packages for this project installed, reduced the risk of
packages interfering with each other. 

*NOTE:* only run `deactivate` when you're done with the virtual environment,
you need to be in the environment to actually use your packages.


## Example Servers:
### Detector:
Don't use this one - it is not updated and should be deprecated.

### Echo Server:
Implements a simple "echo" function by printing out whatever data it receives onto the terminal.
This server removes the wait timer implementation.

If you are not using the FERB Debug mode CLI, it might help to change the FERBware to send a simple byte string to the server, instead of the Grid-EYE output, in order to use this server.

### Grid-EYE Printer:
Print out the received Grid-EYE data as a matrix of temperature values in Celcius.

### Thermal Cam:
Thermal camera demo using the `graphics.py` library. To use it, we need the virtual environment.

After running this server with the script, not much should happen. However, when a FERB unit connects,
a window for the Grid-EYE output should automatically be created, and it should start showing temperature values.
The window will close automatically when the FERB is disconnected.
