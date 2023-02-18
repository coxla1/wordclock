#!/usr/bin/env python3

# Imports
import time
import numpy as np
import datetime
from plugins.abstract import AbstractPlugin
import json
import configparser
import pyowm
from PIL import ImageColor

def indexes(entry):
    '''Words to LED indexes mapping.'''
    word = entry['word']
    index = entry['index']
    length = len(word)
    
    return [*range(index, index + length)]

# TODO : only compatible with 12x12
class TemperaturePlugin(AbstractPlugin):
    def __init__(self, width=16, height=16):
        '''Init the class'''
        super().__init__(width, height)
        self.config = configparser.ConfigParser()
        self.config.read('settings.conf')
        self.section = 'temperature'

        self.fps = 1

        self.api_key = self.config.get(self.section, 'api_key')
        self._location = self.config.get(self.section, 'location')
        
        self.owm = pyowm.OWM(self.api_key).weather_manager()

        self._on_color = ImageColor.getcolor(self.config.get(self.section, 'on_rgb'), 'RGB')
        self._off_color = ImageColor.getcolor(self.config.get(self.section, 'off_rgb'), 'RGB')
        self._rainbow = self.config.getboolean(self.section, 'rainbow')
        
        # TODO : only compatible with 12 columns for now
        self.rainbow_colors = [
            ImageColor.getcolor('#458ac6', 'RGB'),
            ImageColor.getcolor('#00a9d7', 'RGB'),
            ImageColor.getcolor('#00c6ce', 'RGB'),
            ImageColor.getcolor('#2adeb0', 'RGB'),
            ImageColor.getcolor('#9cef8a', 'RGB'),
            ImageColor.getcolor('#f9f871', 'RGB'),
            ImageColor.getcolor('#ffe171', 'RGB'),
            ImageColor.getcolor('#ffca80', 'RGB'),
            ImageColor.getcolor('#ffb896', 'RGB'),
            ImageColor.getcolor('#e4989b', 'RGB'),
            ImageColor.getcolor('#b8819c', 'RGB'),
            ImageColor.getcolor('#846f91', 'RGB'),
        ]
        
        self.__mapping_row_column_to_index()
        self.__construct_numbers_array()

    def __mapping_row_column_to_index(self):
        self.rc_map = np.zeros((self.height, self.width), dtype=np.uint8)
        for index in range(self.number_of_pixels):
            r = (self.number_of_pixels - 1 - index) // self.width
            
            if (r - self.height + 1) % 2 == 0:
                c = (self.number_of_pixels - 1 - index) % self.width
            else:
                c = index % self.width
                
            self.rc_map[r, c] = index
        
        return

    def __construct_numbers_array(self):
        self.numbers = [[] for _ in range(10)]
        
        self.numbers[0] = [
            (2, 1),
            (2, 2),
            (2, 3),
            (2, 4),
            (3, 1),
            (4, 1),
            (5, 1),
            (6, 1),
            (5, 4),
            (7, 1),
            (6, 4),
            (7, 4),
            (8, 1),
            (8, 2),
            (8, 3),
            (8, 4),
            (3, 4),
            (4, 4),
        ]
        
        self.numbers[1] = [
            (2, 4),
            (3, 4),
            (4, 4),
            (5, 4),
            (6, 4),
            (7, 4),
            (8, 4),
        ]
        
        self.numbers[2] = [
            (2, 1),
            (2, 2),
            (2, 3),
            (2, 4),
            (3, 4),
            (4, 4),
            (5, 4),
            (5, 1),
            (5, 2),
            (5, 3),
            (6, 1),
            (7, 1),
            (8, 1),
            (8, 2),
            (8, 3),
            (8, 4),
        ]
        
        self.numbers[3] = [
            (2, 1),
            (2, 2),
            (2, 3),
            (2, 4),
            (3, 4),
            (4, 4),
            (5, 4),
            (5, 1),
            (5, 2),
            (5, 3),
            (6, 4),
            (7, 4),
            (8, 1),
            (8, 2),
            (8, 3),
            (8, 4),
        ]
        
        self.numbers[4] = [
            (2, 4),
            (3, 4),
            (4, 4),
            (5, 4),
            (6, 4),
            (7, 4),
            (8, 4),
            (2, 1),
            (3, 1),
            (4, 1),
            (5, 1),
            (5, 2),
            (5, 3),
        ]
        
        self.numbers[5] = [
            (2, 1),
            (2, 2),
            (2, 3),
            (2, 4),
            (3, 1),
            (4, 1),
            (5, 1),
            (5, 2),
            (5, 3),
            (5, 4),
            (6, 4),
            (7, 4),
            (8, 1),
            (8, 2),
            (8, 3),
            (8, 4),
        ]
        
        self.numbers[6] = [
            (2, 1),
            (2, 2),
            (2, 3),
            (2, 4),
            (3, 1),
            (4, 1),
            (5, 1),
            (5, 2),
            (5, 3),
            (5, 4),
            (6, 1),
            (6, 4),
            (7, 4),
            (7, 1),
            (8, 1),
            (8, 2),
            (8, 3),
            (8, 4),
        ]
        
        self.numbers[7] = [
            (2, 1),
            (2, 2),
            (2, 3),
            (2, 4),
            (3, 4),
            (4, 4),
            (5, 4),
            (6, 4),
            (7, 4),
            (8, 4),
        ]
        
        self.numbers[8] = [
            (2, 1),
            (2, 2),
            (2, 3),
            (2, 4),
            (3, 1),
            (4, 1),
            (5, 1),
            (5, 2),
            (5, 3),
            (6, 1),
            (5, 4),
            (7, 1),
            (6, 4),
            (7, 4),
            (8, 1),
            (8, 2),
            (8, 3),
            (8, 4),
            (3, 4),
            (4, 4),
        ]
        
        self.numbers[9] = [
            (2, 1),
            (2, 2),
            (2, 3),
            (2, 4),
            (3, 4),
            (4, 4),
            (5, 4),
            (6, 4),
            (7, 4),
            (8, 4),
            (3, 1),
            (4, 1),
            (5, 1),
            (5, 2),
            (5, 3),
        ]
        
        self.minus = [
            (5, 1),
            (5, 2),
            (5, 3),
            (5, 4),
            (6, 1),
            (6, 2),
            (6, 3),
            (6, 4),
        ]
        
        self.degree = [
            (2, 7),
            (2, 8),
            (3, 7),
            (3, 8),
        ]

    @property
    def on_color(self):
        return self._on_color

    @on_color.setter
    def on_color(self, color):
        self._on_color = color

    @property
    def off_color(self):
        return self._off_color

    @off_color.setter
    def off_color(self, color):
        self._off_color = color
        
    @property
    def rainbow(self):
        return self._rainbow

    @rainbow.setter
    def rainbow(self, boolean):
        self._rainbow = boolean
    
    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    @property
    def topics(self):
        return [
            'wordclock/plugin/temperature/on',
            'wordclock/plugin/temperature/off',
            'wordclock/plugin/temperature/rainbow',
            'wordclock/plugin/temperature/location',
        ]

    @property
    def subscription_filter(self):
        return 'wordclock/plugin/temperature/#'

    def callback(self, client, userdata, msg):
        print('%s %s' % (msg.topic, msg.payload))
        
        if msg.topic == 'wordclock/plugin/temperature/rainbow':
            try:
                boolean = bool(msg.payload.decode('utf-8'))
                self.rainbow = boolean
                self.config.set(self.section, 'rainbow', boolean)
            except:
                print('Invalid boolean')
        
        elif msg.topic == 'wordclock/plugin/temperature/location':
            try:
                location = msg.payload.decode('utf-8')
                old_location = self.location
                self.location = location
                self.__getTemperature()
                self.config.set(self.section, 'location', location)
                     
            except pyowm.commons.exceptions.PyOWMError:
                print('Invalid location')
                self.location = old_location
                
        else:
            try:
                color = ImageColor.getcolor(msg.payload.decode('utf-8'), 'RGB')
                if msg.topic == 'wordclock/plugin/clock/on':
                    self.on_color = color
                    self.config.set(self.section, 'on_rgb', rgb2hex(self.on_color))
                elif msg.topic == 'wordclock/plugin/clock/off':
                    self.off_color = color
                    self.config.set(self.section, 'off_rgb', rgb2hex(self.off_color))
            except ValueError as ve:
                print('Invalid RGB value')

        with open('settings.conf', 'w') as configfile:
            self.config.write(configfile)

    def update(self, dt):
        '''Update the source. Checks current temperature and refreshes the internal buffer.'''
        try:
            temp = self.__getTemperature()
        except pyowm.commons.exceptions.PyOWMError:
            print('Error with OpenWeatherMap, maybe bad API key ?')
            temp = -1
        
        self._buffer = self.__construct_buffer(temp)

    def __getTemperature(self):
        '''Get current temperature information.'''
        observation = self.owm.weather_at_place(self._location)
        temp = observation.weather.temperature('celsius')['temp']
        
        return round(temp)

    def __constructIndexes(self, temp):
        '''Get array of indexes which map which letters to light up.'''
        digit1 = []
        digit2 = []
        degree = []
        
        if 0 <= temp < 10:
            if temp == 1:
                offset = 1
                offsetdeg = 0
            else:
                offset = 2
                offsetdeg = 1
                
            for r, c in self.numbers[temp]:
                digit1.append(self.rc_map[r, c+offset])
            
            for r, c in self.degree:
                degree.append(self.rc_map[r, c+offsetdeg])
        
        elif temp < 0: 
            if temp <= -10: # should not happen
                temp = -9
            offset1 = -1
            if -temp == 1:
                offset2 = 1
                offsetdeg = 0
            else:
                offset2 = 4
                offsetdeg = 3
            
            for r, c in self.minus:
                digit1.append(self.rc_map[r, c+offset1])
                
            for r, c in self.numbers[-temp]:
                digit2.append(self.rc_map[r, c+offset2])
            
            for r, c in self.degree:
                degree.append(self.rc_map[r, c+offsetdeg])
        
        else:
            if temp >= 100: # should not happen
                temp = 99
            offset1 = -1
            if temp % 10 == 1:
                offset2 = 1
                offsetdeg = 0
            else:
                offset2 = 4
                offsetdeg = 3
            
            for r, c in self.numbers[temp // 10]:
                digit1.append(self.rc_map[r, c+offset1])
                
            for r, c in self.numbers[temp % 10]:
                digit2.append(self.rc_map[r, c+offset2])
            
            for r, c in self.degree:
                degree.append(self.rc_map[r, c+offsetdeg])
        
        return (
            digit1
            + digit2
            + degree
        )

    def __construct_buffer(self, temp):
        '''Construct display buffer given the current time and weekday.'''
        buffer = np.zeros((self.number_of_pixels, 3), dtype=np.uint8)
        led_indexes = self.__constructIndexes(temp)
        
        for index in range(self.number_of_pixels):
            if index in led_indexes:
                if self.rainbow:
                    row = (self.number_of_pixels - 1 - index) // self.width
                    if (row - self.height + 1) % 2 == 0:
                        column = (self.number_of_pixels - 1 - index) % self.width
                    else:
                        column = index % self.width
                    
                    buffer[index] = self.rainbow_colors[column]
                
                else:
                    buffer[index] = self.on_color
                
            else:
                buffer[index] = self.off_color
        
        return buffer
