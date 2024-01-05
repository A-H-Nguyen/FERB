#!/bin/bash

# Exit on error
set -e

# Number of cores when running make
JNUM=4

# Where will the output go?
OUTDIR="$(pwd)"

# Install dependencies
SDK_DEPS="cmake gcc-arm-none-eabi gcc g++"
OPENOCD_DEPS="gdb-multiarch automake autoconf build-essential texinfo libtool libftdi-dev libusb-1.0-0-dev"
UART_DEPS="minicom"

# Build full list of dependencies
DEPS="$SDK_DEPS $OPENOCD_DEPS $UART_DEPS"

echo "Installing Dependencies"
sudo apt update
sudo apt install -y $DEPS

# Clone sw repos
GITHUB_PREFIX="https://github.com/raspberrypi/"
GITHUB_SUFFIX=".git"
SDK_BRANCH="master"

# We might never need to use pico-extras, but it won't hurt to have it for now
for REPO in sdk extras
do
    DEST="$OUTDIR/pico-$REPO"

    if [ -d $DEST ]; then
        echo "$DEST already exists so skipping"
    else
        REPO_URL="${GITHUB_PREFIX}pico-${REPO}${GITHUB_SUFFIX}"
        echo "Cloning $REPO_URL"
        git clone -b $SDK_BRANCH $REPO_URL

        # Any submodules
        cd $DEST
        git submodule update --init
        cd $OUTDIR

        # Define PICO_SDK_PATH in ~/.bashrc
        VARNAME="PICO_${REPO^^}_PATH"
        echo "Adding $VARNAME to ~/.bashrc"
        echo "export $VARNAME=$DEST" >> ~/.bashrc
        export ${VARNAME}=$DEST
    fi
done

cd $OUTDIR

# we also need the pico_sdk_import.cmake file in order to import the SDK into our project
cp $OUTDIR/pico-sdk/external/pico_sdk_import.cmake lib/.


# Picoprobe and picotool - these are used for debugging
# I will hopefully test these out later
# for REPO in picoprobe picotool
# do
#     DEST="$OUTDIR/$REPO"
#     REPO_URL="${GITHUB_PREFIX}${REPO}${GITHUB_SUFFIX}"
#     git clone $REPO_URL
# 
#     # Build both
#     cd $DEST
#     git submodule update --init
#     mkdir build
#     cd build
#     cmake ../
#     make -j$JNUM
# 
#     if [[ "$REPO" == "picotool" ]]; then
#         echo "Installing picotool to /usr/local/bin/picotool"
#         sudo cp picotool /usr/local/bin/
#     fi
# 
#     cd $OUTDIR
# done

# Build OpenOCD
# if [ -d openocd ]; then
#     echo "openocd already exists so skipping"
#     SKIP_OPENOCD=1
# fi
# 
# if [[ "$SKIP_OPENOCD" == 1 ]]; then
#     echo "Won't build OpenOCD"
# else
#     echo "Building OpenOCD"
#     cd $OUTDIR
#     # Should we include picoprobe support (which is a Pico acting as a debugger for another Pico)
#     INCLUDE_PICOPROBE=1
#     OPENOCD_BRANCH="rp2040-v0.12.0"
#     OPENOCD_CONFIGURE_ARGS="--enable-ftdi --enable-sysfsgpio --enable-bcm2835gpio"
#     if [[ "$INCLUDE_PICOPROBE" == 1 ]]; then
#         OPENOCD_CONFIGURE_ARGS="$OPENOCD_CONFIGURE_ARGS --enable-picoprobe"
#     fi
# 
#     git clone "${GITHUB_PREFIX}openocd${GITHUB_SUFFIX}" -b $OPENOCD_BRANCH --depth=1
#     cd openocd
#     ./bootstrap
#     ./configure $OPENOCD_CONFIGURE_ARGS
#     make -j$JNUM
#     sudo make install
# fi
# 
# cd $OUTDIR
