#!/usr/bin/env python3

import numpy as np
import sys
from display.abstract_display import AbstractDisplay
import configparser

import board
import neopixel

# LED strip configuration:
LED_PIN         = board.D18
LED_ORDER       = neopixel.GRB  # neopixel.GRB if colors are revert


class WS2812B(AbstractDisplay):
    def __init__(self, width=16, height=16):
        super().__init__(width, height)

        self.config = configparser.ConfigParser()
        self.config.read('settings.conf')
        self.section = 'display'

        self._brightness = self.config.getfloat(self.section, 'brightness')
        
        # Create NeoPixel object with appropriate configuration.
        self.strip = neopixel.NeoPixel(
            LED_PIN,
            self.number_of_pixels,
            brightness = 1,
            pixel_order = LED_ORDER,
            auto_write = False
        )
        
        self.strip.brightness = self._brightness
        
        # Intialize the library (must be called once before other functions).
        # self.strip.begin()
    
    def show(self):
        '''Iterate through the buffer and assign each LED index a color from the buffer'''
        for index in range(self.number_of_pixels):
            color = self.buffer[index]
            self.strip[index] = tuple(color)
        
        self.strip.brightness = self._brightness
        self.strip.show()
        return


if __name__ == '__main__':
    display = WS2812B()
    display.create_test_pattern()
    display.show()
    import time

    time.sleep(5)
