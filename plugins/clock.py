#!/usr/bin/env python3

# Imports
import time
import numpy as np
import datetime
from plugins.abstract import AbstractPlugin
import json
import configparser
from PIL import ImageColor

def indexes(entry):
    '''Words to LED indexes mapping.'''
    word = entry['word']
    index = entry['index']
    length = len(word)
    
    return [*range(index, index + length)]


def rgb2hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


class ClockPlugin(AbstractPlugin):
    def __init__(self, width=16, height=16):
        '''Init the class'''
        super().__init__(width, height)
        self.config = configparser.ConfigParser()
        self.config.read('settings.conf')
        self.section = 'clock'

        self.fps = 5

        self._sim_hour = 0
        self._sim_minute = 0
        self._sim_second = 0
        self._sim_weekday = 0

        self.minutes = []
        self.additional_minutes = []
        self.hours = []
        self.weekdays = []
        self.prefix = []
        # self.soon = []
        # self.signature = []
        self.simulate = self.config.getboolean(self.section, 'simulate')
        self._on_color = ImageColor.getcolor(self.config.get(self.section, 'on_rgb'), 'RGB')
        self._off_color = ImageColor.getcolor(self.config.get(self.section, 'off_rgb'), 'RGB')
        self._day_color = ImageColor.getcolor(self.config.get(self.section, 'day_rgb'), 'RGB')
        self._minute_color = ImageColor.getcolor(self.config.get(self.section, 'minute_rgb'), 'RGB')
        # self._signature_color = ImageColor.getcolor(self.config.get(self.section, 'signature_rgb'), 'RGB')
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
        
        self.additional_minutes_colors = [
            ImageColor.getcolor('#e4989b', 'RGB'),
            ImageColor.getcolor('#458ac6', 'RGB'),
            ImageColor.getcolor('#00c6ce', 'RGB'),
            ImageColor.getcolor('#846f91', 'RGB'),
        ]
        
        self.additional_minutes_index = []
        self.weekdays_index = []

        self.__construct_word_arrays()

    def __construct_word_arrays(self):
        f = open('layouts/french.json', encoding='utf-8')
        layout = json.load(f)

        self.prefix = indexes(layout['prefix']['it']) + indexes(layout['prefix']['is'])
        # self.soon = indexes(layout['prefix']['soon'])
        # self.signature = indexes(layout['others']['signature'])

        self.minutes = [
            indexes(layout['minutes']['oclock']),
            indexes(layout['minutes']['five']),
            indexes(layout['minutes']['ten']),
            indexes(layout['minutes']['and']) + indexes(layout['minutes']['quarter']),
            indexes(layout['minutes']['twenty']),
            indexes(layout['minutes']['twenty']) + indexes(layout['minutes']['five']),
            indexes(layout['minutes']['and']) + indexes(layout['minutes']['half']),
            indexes(layout['minutes']['to'])
            + indexes(layout['minutes']['twenty'])
            + indexes(layout['minutes']['five']),
            indexes(layout['minutes']['to']) + indexes(layout['minutes']['twenty']),
            indexes(layout['minutes']['to'])
            + indexes(layout['minutes']['the'])
            + indexes(layout['minutes']['quarter']),
            indexes(layout['minutes']['to']) + indexes(layout['minutes']['ten']),
            indexes(layout['minutes']['to']) + indexes(layout['minutes']['five']),
        ]
        self.additional_minutes = [
            [],
            indexes(layout['minutes']['one']),
            indexes(layout['minutes']['one'])
            + indexes(layout['minutes']['two']),
            indexes(layout['minutes']['one'])
            + indexes(layout['minutes']['two'])
            + indexes(layout['minutes']['three']),
            indexes(layout['minutes']['one'])
            + indexes(layout['minutes']['two'])
            + indexes(layout['minutes']['three'])
            + indexes(layout['minutes']['four']),
        ]
        self.additional_minutes_index = [
            layout['minutes']['one']['index'],
            layout['minutes']['two']['index'],
            layout['minutes']['three']['index'],
            layout['minutes']['four']['index'],
        ]
        self.hours = [
            indexes(layout['hours']['midnight']),
            indexes(layout['hours']['one']) + indexes(layout['hours']['hour']),
            indexes(layout['hours']['two']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['three']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['four']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['five']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['six']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['seven']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['eight']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['nine']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['ten']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['eleven']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['midday']),
            indexes(layout['hours']['one']) + indexes(layout['hours']['hour']),
            indexes(layout['hours']['two']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['three']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['four']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['five']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['six']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['seven']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['eight']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['nine']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['ten']) + indexes(layout['hours']['hours']),
            indexes(layout['hours']['eleven']) + indexes(layout['hours']['hours']),
        ]
        self.weekdays = [
            indexes(layout['day']['monday']),
            indexes(layout['day']['tuesday']),
            indexes(layout['day']['wednesday']),
            indexes(layout['day']['thursday']),
            indexes(layout['day']['friday']),
            indexes(layout['day']['saturday']),
            indexes(layout['day']['sunday']),
        ]
        self.weekdays_index = [
            layout['day']['monday']['index'],
            layout['day']['tuesday']['index'],
            layout['day']['wednesday']['index'],
            layout['day']['thursday']['index'],
            layout['day']['friday']['index'],
            layout['day']['saturday']['index'],
            layout['day']['sunday']['index'],
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
    def day_color(self):
        return self._day_color

    @day_color.setter
    def day_color(self, color):
        self._day_color = color
        
    @property
    def minute_color(self):
        return self._minute_color

    @minute_color.setter
    def minute_color(self, color):
        self._minute_color = color

    # @property
    # def signature_color(self):
        # return self._signature_color

    # @signature_color.setter
    # def signature_color(self, color):
        # self._signature_color = color
        
    @property
    def rainbow(self):
        return self._rainbow

    @rainbow.setter
    def rainbow(self, boolean):
        self._rainbow = boolean

    @property
    def topics(self):
        return [
            'wordclock/plugin/clock/on',
            'wordclock/plugin/clock/off',
            'wordclock/plugin/clock/day',
            'wordclock/plugin/clock/minute',
            'wordclock/plugin/clock/rainbow',
            # 'wordclock/plugin/clock/signature'
        ]

    @property
    def subscription_filter(self):
        return 'wordclock/plugin/clock/#'

    def callback(self, client, userdata, msg):
        print('%s %s' % (msg.topic, msg.payload))
        
        if msg.topic == 'wordclock/plugin/clock/rainbow':
            try:
                boolean = bool(msg.payload.decode('utf-8'))
                self.rainbow = boolean
                self.config.set(self.section, 'rainbow', boolean)
            except:
                print('Invalid boolean')
                
        else:
            try:
                color = ImageColor.getcolor(msg.payload.decode('utf-8'), 'RGB')
                if msg.topic == 'wordclock/plugin/clock/on':
                    self.on_color = color
                    self.config.set(self.section, 'on_rgb', rgb2hex(self.on_color))
                elif msg.topic == 'wordclock/plugin/clock/off':
                    self.off_color = color
                    self.config.set(self.section, 'off_rgb', rgb2hex(self.off_color))
                elif msg.topic == 'wordclock/plugin/clock/day':
                    self._day_color = color
                    self.config.set(self.section, 'day_rgb', rgb2hex(self.day_color))
                elif msg.topic == 'wordclock/plugin/clock/minute':
                    self._minutes_color = color
                    self.config.set(self.section, 'minute_rgb', rgb2hex(self.minute_color))
                # elif msg.topic == 'wordclock/plugin/clock/signature':
                    # self._signature_color = color
                    # self.config.set(self.section, 'signature_rgb', rgb2hex(self.signature_color))
            except ValueError as ve:
                print('Invalid RGB value')

        with open('settings.conf', 'w') as configfile:
            self.config.write(configfile)

    def update(self, dt):
        '''Update the source. Checks current time and refreshes the internal buffer.'''
        hour, minute, second, weekday = (
            self.__getCurrentTime() if not self.simulate else self.__getSimulateTime()
        )
        self._buffer = self.__construct_buffer(hour, minute, second, weekday)

    def __getCurrentTime(self):
        '''Get current time information.'''
        now = datetime.datetime.now().time()
        weekday = datetime.datetime.now().weekday()
        return now.hour, now.minute, now.second, weekday

    def __getSimulateTime(self):
        '''Get simulated time information.'''
        self._sim_hour += 1
        if self._sim_hour % 24 == 0:
            self._sim_minute += 1
            self._sim_weekday += 1
            if self._sim_minute % 60 == 0:
                self._sim_second += 30

        return (
            self._sim_hour % 24,
            self._sim_minute % 60,
            self._sim_second % 60,
            self._sim_weekday % 7,
        )

    def __constructIndexes(self, hour, minute, second, weekday):
        '''Get array of indexes which map with words to light up.'''
        # Check if an hour should be added
        additional_hour = 1 if (minute >= 35) else 0

        hour_index = (hour + additional_hour) % 24
        minute_index = (minute % 60) // 5
        additional_minute_index = minute % 5
        # soon = []
        # if minute / 5 % 1 > 0.7:
        #     minute_index += 1
        #     soon = self.soon
        
        return (
            self.prefix
            + self.minutes[minute_index]
            + self.additional_minutes[additional_minute_index]
            + self.hours[hour_index]
            + self.weekdays[weekday]
            # + soon
            # + self.signature
        )

    def __construct_buffer(self, hour, minute, second, weekday):
        '''Construct display buffer given the current time and weekday.'''
        buffer = np.zeros((self.number_of_pixels, 3), dtype=np.uint8)
        led_indexes = self.__constructIndexes(hour, minute, second, weekday)
        
        for index in range(self.number_of_pixels):
            if index in led_indexes:
                if index in self.additional_minutes_index:
                    if self.rainbow:
                        buffer[index] = self.additional_minutes_colors[self.additional_minutes_index.index(index)]
                    else:
                        buffer[index] = self.minute_color
                
                elif index in self.weekdays_index:
                    buffer[index] = self.day_color
                
                else:
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
