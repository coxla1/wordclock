#!/usr/bin/env python3

import board
import neopixel

# LED strip configuration:
LED_PIN         = board.D18
LED_ORDER       = neopixel.GRB  # neopixel.GRB if colors are revert

strip = neopixel.NeoPixel(
        LED_PIN,
        144,
        brightness = 0,
        pixel_order = LED_ORDER,
        auto_write = False
    )

strip.show()