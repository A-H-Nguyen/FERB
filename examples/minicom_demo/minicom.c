/**
 * Maybe I'll make this Demo do more stuff later
 */

#include <stdio.h>

#include "pico/stdlib.h"
// #include "pico/cyw43_arch.h"

int main() {
    stdio_init_all();

    while (true) {
        printf("Hello, world!\n");
        sleep_ms(1000);
    }
}