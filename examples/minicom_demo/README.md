# minicom Guide

## Installing minicom
Before we can use minicom to interface with the Serial output of the Rasperru Pi Pico or Pico W, we need to make sure it's installed.
The command to install minicom should already be run by the ferb setup script, but you can verify if it's installed a couple of ways:

```bash
# Option 1:
which minicom

# Option 2:
minicom --version
```

If minicom is not installed on your system just run the following:

```bash
sudo apt update
sudp apt install minicom
```

## Setting up minicom
This will change depending on your system.

### Native Linux install
I haven't tested this myself, but [this guide](https://www.electronicshub.org/raspberry-pi-pico-serial-programming/) should work.
You'll end up running the `minicom -D` command, but since this is for a Linux install on a physical machine, 
you need to set the baud rate of the serial port.

### Virtual Linux Machine
*NOTE:* This is different from WSL!

This will heavily depend on what VM platform you're using. In general, you should be able to pass USB devices from your host OS
to your VM using your VM platform. Common VM platforms include [Oracle's VirtualBox](https://www.virtualbox.org/) and 
[VMware](https://customerconnect.vmware.com/en/downloads/#all_products). I am partial to VirtualBox as I've used it before, and
it's really easy to set up on your own.
For VMware, I've found [this guide](https://www.electromaker.io/blog/article/getting-started-with-the-raspberry-pi-pico-w-cc-sdk)
from electromaker.io which shows you how to set up the whole Pico SDK toolchain on an Ubuntu VM. Near the end of the guide,
the author also covers how to use minicom, and it looks very simple.

Just install minicom:

```bash
sudo apt install minicom 
```

And you should be able to use it once you have connected your flashed Pico to the VM.

### WSL
Also known as "Windows Subsystem for Linux". I don't actually recommend using WSL for this. 
As you can see from the length of this section of the guide, using WSL to develop for the Pico is a pain in the ass.
If you're intent with using WSL, then read on. Another quick note, WSL2 is the default version now, but I think people 
still use WSL1 sometimes. For our use case, I'll assume you're on WSL2.

Connecting a USB device from Windows to a WSL Linux distro is easier said than done.
Microsoft has [this hand guide](https://learn.microsoft.com/en-us/windows/wsl/connect-usb). 
If you look at that guide, you'll see that  we need to install the usbipd program on the *Windows* side. 
So, open your powershell in *Administrator Mode*. This is important! **usbipd won't work if you're not running it as Admin.**

Now usually I would just leave this link and tell you to follow it, however ALL of their usbipd commands are wrong. 
I'm not joking. The usbipd program no longer needs the wsl keyword to run commands, but the Microsoft guide has not been updated to reflect this.

Before we do anything, make sure WSL works:
```
PS C:\Users\AnNgu> wsl --list -v
  NAME                   STATE           VERSION
* Ubuntu                 Running         2
  docker-desktop         Stopped         2
  docker-desktop-data    Stopped         2
  Debian                 Stopped         1
```
If you run `wsl --list -v` and it doesn't look somewhat like this, something might be wrong.
So go fix that and come back. Don't worry, I'm not going anywere.

#### Installing usbipd
There are a couple of ways to install usbipd and the easiet way is to use `winget`:
```
winget install --interactive --exact dorssel.usbipd-win
```
You might not have `winget` installed, so either install it, or use the aforementioned 
[Microsoft guide](https://learn.microsoft.com/en-us/windows/wsl/connect-usb) to install `usbipd`.

#### Using usbipd
Now that we have usbipd and we have our *administrator* powershell open, let's use it.

First make sure you've already flashed your Raspberry Pi Pico with whatever code you want to run.
Then, let's run this command:

```powershell
usbipd list
```

The ouput should be something like this:
```
Connected:
BUSID  VID:PID    DEVICE                                                        STATE
5-1    05ac:024f  USB Input Device                                              Not shared
5-2    046d:c53f  USB Input Device                                              Not shared
5-3    2e8a:000a  USB Serial Device (COM3), Reset                               Not shared

Persisted:
GUID                                  DEVICE
d8128551-aa75-410b-a175-04dfe10d66a3  USB Mass Storage Device, RP2 Boot
```

In my case, my Pico is the COM3 USB device. I'm not sure if the COM port number matters, and we'll see why soon.

Anyways, if you look at the "STATE" column, you'll see that all of these devices are marked as "Not shared," which
means that we will not be able to send these devices to our WSL distro. No big deal. We just have to run the "bind" command.
But hold on! If you look at the command below, you can see we need a BUS ID after the -b flag. Of course, you also probably already
saw that the output of `usbipd list` gives us all the BUSIDs, so just substitute for whatever ID your Pico has (hyphen included).

```powershell
usbipd bind -b <BUSID>
```

Keeping with my example, I would use `BUSID=5-3` so my command would end up being `usbipd bind -b 5-3`.
Now, if you were to run the list command again, you'll see that under "STATE," your device will now be listed as "Shared"

We can finally connect our Pico to our WSL!

```powershell
usbipd attach -b <BUSID> -w
```

If it works, you should see an output that looks something like this:

```
usbipd: info: Using WSL distribution 'Ubuntu' to attach; the device will be available in all WSL 2 distributions.
usbipd: info: Using IP address 172.22.240.1 to reach the host.
```

Do make sure that usbipd attaches to the correct distro. If you want, you can specify which distro to attach to like so:

```powershell
usbipd attach -b <BUSID> -w <[DISTRIBUTION]>
```
So, you could have something like: `usbipd attach -b 5-3 -w Ubuntu`

Once you're done using your usb device, you can run:

```powershell
usbipd detach -b <BUSID>
```

Or... you can just unplug the Pico...

## Okay, now we can use minicom
In your distro of choice (I'm using Ubuntu) let's start by verifying that our USB device is connected:

```bash
lsusb
```

If this command fails, you'll either have to use a different method to verify, or you can try to fix it.
In any case, the output should be something like this:

```
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 007: ID 2e8a:000a Raspberry Pi Pico
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

Now, let's run the minicom command:

```bash
# For virutal machines
sudo minicom -D /dev/ttyACM0

# For physical machines
sudo minicom -b 115200 -o -D /dev/ttyACM0
```

All USB devices should be within the /dev/ directory, however your Pico might not be found at /dev/ttyACM0. 
From my testing, my Pico was located at /dev/ttyACM0, but your results may vary, especially because so far I have
only tested things with WSL. If you look at the two different commands, for Linux on a physical machine, you need
to set the baud rate using -b. This is the same as if you're using Arduino's Serial Monitor.

If everything is correct, you should see your terminal change to something like this (here I am using the helloworld example):

```
Welcome to minicom 2.8

OPTIONS: I18n 
Port /dev/ttyACM0, 09:39:07

Press CTRL-A Z for help on special keys

Hello, world!
Hello, world!
Hello, world!
Hello, world!
Hello, world!
Hello, world!
Hello, world!
Hello, world!                                 
``` 
