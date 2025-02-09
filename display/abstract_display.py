#!/usr/bin/env python3

import abc
import numpy as np
import time
import configparser


class AbstractDisplay(abc.ABC):
    def __init__(self, width=16, height=16):
        self.width = width
        self.height = height
        self.number_of_pixels = self.height * self.width
        
        self.config = configparser.ConfigParser()
        self.config.read('settings.conf')
        self.section = 'display'
        
        self._buffer = np.zeros((self.number_of_pixels, 3), dtype=np.uint8)
        self._brightness = self.config.getfloat(self.section, 'brightness')

    @property
    def buffer(self):
        '''The buffer contains the rgb data to be displayed.'''
        return self._buffer

    @buffer.setter
    def buffer(self, value):
        if isinstance(value, np.ndarray):
            if self._buffer.shape == value.shape:
                self._buffer = value

    def clear_buffer(self):
        '''Erase the buffer and fill it with zeros.'''
        self._buffer = np.zeros_like(self._buffer)

    @abc.abstractmethod
    def show(self, gamma=False):
        '''Display the content of the buffer.'''

    @property
    def topics(self):
        '''Get an array of of topics which the display driver accepts'''
        return ['wordclock/display/brightness']

    @property
    def subscription_filter(self):
        '''Topic filter used to trigger the callback method'''
        return 'wordclock/display/#'

    def callback(self, client, userdata, msg):
        '''Method which should be called when a topic is updated which matches the subscription filter'''
        try:
            if msg.topic == 'wordclock/display/brightness':
                txt = msg.payload.decode('utf-8')
                b = float(txt)
                self._brightness = b
                self.config.set(self.section, 'brightness', txt)
        except ValueError as ve:
            print('Invalid brightness value')

    @property
    def brightness(self):
        '''Get current brightness level (0.0 to 1.0).'''
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if value > 1.0:
            self._brightness = 1.0
        elif value < 0.0:
            self._brightness = 0
        else:
            self._brightness = value

    def set_pixel_at_index(self, index, color):
        if (index < 0) or (index > self.number_of_pixels):
            return
        index *= 3
        self._buffer.put([index, index + 1, index + 2], color)

    def set_pixel_at_coord(self, x, y, color):
        if (x < 0) or (x >= self.width) or (y < 0) or (y >= self.height):
            return
        self._buffer[y, x] = color

    def set_buffer_with_flat_values(self, rgb_values):
        rgb_values = np.array(rgb_values, dtype=np.uint8)
        rgb_values.resize((self.number_of_pixels * 3,), refcheck=False)
        rgb_values = rgb_values.reshape(self.height, self.width, 3)
        self._buffer = rgb_values

    def create_test_pattern(self):
        self.clear_buffer()
        number_of_leds = self.width * self.height
        for i in range(number_of_leds):
            self.set_pixel_at_index(i % self.number_of_pixels, self.wheel(i))

    def wheel(self, pos):
        '''Input a value 0 to 255 to get a color value. The colours are a transition r - g - b - back to r'''
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

    def run_benchmark(self):
        total = 0
        repeat = self.number_of_pixels * 10
        for i in range(repeat):
            start = time.time()
            self.set_pixel_at_index(i % self.number_of_pixels, (255, 255, 255))
            self.clear_buffer()
            end = time.time()
            diff = end - start
            total = total + diff
        print(
            '{:.2f}s for {} iterations. {:d} refreshs per second'.format(
                total, repeat, int(repeat / total)
            )
        )
        self.clear_buffer()
        self.show()
