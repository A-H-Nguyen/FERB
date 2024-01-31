/**
 * Maybe I'll make this Demo do more stuff later
 */

#include <iostream>

#include "pico/stdlib.h"
// #include "pico/cyw43_arch.h"

int main() {
    stdio_init_all();

    while (true) {
        std::cout << "Hello world" << std::endl;
        sleep_ms(1000);
    }
}