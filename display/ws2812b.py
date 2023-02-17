#!/usr/bin/env python3

import numpy as np
import sys
from display.abstract_display import AbstractDisplay
import configparser

import board
import neopixel

# LED strip configuration:
LED_PIN         = 18            # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN         = 10            # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
# LED_FREQ_HZ     = 800000        # LED signal frequency in hertz (usually 800khz)
# LED_DMA         = 10            # DMA channel to use for generating signal (try 10)
# LED_BRIGHTNESS  = 0.3           # Set to 0 for darkest and 1 for brightest
LED_ORDER       = neopixel.RGB  # neopixel.GRB if colors are revert
# LED_CHANNEL     = 0             # set to '1' for GPIOs 13, 19, 41, 45 or 53


class WS2812B(AbstractDisplay):
    def __init__(self, width=16, height=16):
        super().__init__(width, height)

        self.config = configparser.ConfigParser()
        self.config.read('settings.conf')
        self.section = 'display'

        self._brightness = self.config.getfloat(self.section, 'brightness')
        self.reverse_mirror = self.config.getboolean(self.section, 'reverse_mirror')

        # Create NeoPixel object with appropriate configuration.
        self.strip = neopixel.NeoPixel(
            LED_PIN,
            self.widht * self.height,
            brightness = self.brightness,
            pixel_order = LED_ORDER,
            auto_write = False
        )

        # Intialize the library (must be called once before other functions).
        # self.strip.begin()

    def show(self):
        '''Iterate through the buffer and assign each LED index a color from the buffer'''
        index = 0
        for j in range(self.width):
            for i in range(self.height):
                i2 = self.height - 1 - i
                j2 = j
                if i2 % 2 == 0:
                    j2 = self.width - 1 - j
                
                color = self.buffer[i2, j2]
                self.strip[i2 * self.width + j2] = tuple(color)
                
        self.strip.show()
        return


if __name__ == '__main__':
    display = WS2812B()
    display.create_test_pattern()
    display.show()
    import time

    time.sleep(5)
