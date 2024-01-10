add_executable(minicom_demo
    minicom.cpp
)

target_link_libraries(minicom_demo
    pico_stdlib
    # pico_cyw43_arch_none
)

# enable usb output, disable uart output
pico_enable_stdio_usb(minicom_demo 1)
pico_enable_stdio_uart(minicom_demo 0)

# create map/bin/hex file etc.
pico_add_extra_outputs(minicom_demo)