# FERB Old Ver.
The original plan for the FERB project was to use the Raspberry Pi Pico C/C++ SDK. However, we switched to Micropython as it was easier to
rapidly prototype with.

## How to Use the old FERB code
This was only ever tested using cmake on Linux, so mileage may vary when trying to compile on a different operating system.

If you want to try it out, or if we need to reimplment this for whatever reason, follow the directions in the next section

## Flashing and Compiling the FERBware
The heart of the FERB is a Raspberry Pi Pico W. Simply build and compile the CMake project, and then flash your Pico with the generated uf2.

In order to flash a Raspberry Pi Pico (or Pico W), hold the BOOTSEL button on the Pico, and then plug it into whatever computer you compiled this code on.
The Pico shjould appear in your files as a USB drive named something like `RPI-RP2`. Once you find it, drag and drop the FERB uf2 into the Pico directory.
This should cause the Pico to automatically reset and start running your code. You can use the code in `examples/` to test you Pico.

### Setup
Before you can compile code for the FERB uf2, you need to make sure you have the correct tools and libraries installed, namely the pico-sdk.

First, make sure you have Python 3.9 or later installed.

Next, run `./ferb_setup.sh` (*NOTE:* from this point on, make sure to run everything INSIDE the directory for this repo on you local machine!)

The setup script will ensure you have the necessary programs such as cmake and the GNU C/C++ compilers.
It will also automatically clone the repositories for the pico-sdk, and pico-extras library, as well as their respective submodules.

### Using CMake
Using CMake is actually pretty easy imho.

First, create a `build` directory:
```
mkdir build
cd build
```
This directory will house all the auto-generated build files that the `cmake` command will produce, as well as all compiled files.
Having a seperate build directory will just serve to make things more organized, and it's also just the standard practice for CMake projects.

From here, look inside the build directory - you should see a folder called `src` and a folder called `examples`.
`src` will house the final code for FERB, and is currently WIP. `examples` has quick code examples to run on the Raspberry Pi Pico W, for testing specific hardware functionalities.

#### Building the Blink Example
Go to the `blink` directory:
```
cd examples/blink
```

You'll see that CMake generated a Makefile for us, so let's use it:
```
make
```

The terminal will spit out a lot of stuff, so be sure to show your non-programmer friends to impress them, and make you think that you're way better at programming than you actually are.
Oh, and there should also be a `blink.uf2` file now, so go ahead and flash your Pico using it, as we discussed earlier.
