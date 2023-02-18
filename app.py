#!/user/bin/env python3
'''
Main entry point of the tidsram project.
Runs the main game-loop.
'''

# Imports
import os
import platform
import sys
import abc
import numpy as np
import time
import datetime
import configparser
import pygame
import io
from io import BytesIO
from pathlib import Path
from plugins.clock import ClockPlugin
from plugins.temperature import TemperaturePlugin
import paho.mqtt.client as mqtt

# Global variables
DISPLAY_WIDTH = 12
DISPLAY_HEIGHT = 12


class WordClock:
    def __init__(self):
        # Change working directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        if is_raspberrypi():
            from display.ws2812b import WS2812B

            self.display = WS2812B(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        else:
            from display.computer import Computer

            self.display = Computer(DISPLAY_WIDTH, DISPLAY_HEIGHT, 5, 50)
        
        config = configparser.ConfigParser()
        config.read('settings.conf')
        self.enable_temperature = config.getboolean('temperature', 'enable')
        
        # Sources
        self.clock = ClockPlugin(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        
        if self.enable_temperature:
            self.temperature = TemperaturePlugin(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        
        self.source = self.clock
        self.display.brightness = 1
        

    # The callback for when the client receives a CONNACK response from the server.
    def on_mqtt_connect(self, client, userdata, flags, rc):
        print('Connected with result code ' + str(rc))

        # Subscribe to topics from the display
        for topic in self.display.topics:
            client.subscribe(topic)

        # Subscribe to topics from plugins
        for topic in self.source.topics:
            client.subscribe(topic)

        # Add callback for the display
        client.message_callback_add(
            self.display.subscription_filter, self.display.callback
        )

        # Add callback for plugins using filter
        client.message_callback_add(
            self.source.subscription_filter, self.source.callback
        )

    # The callback for when a PUBLISH message is received from the server.
    def on_mqtt_message(self, client, userdata, msg):
        print(msg.topic + ' ' + str(msg.payload))

    def mainloop(self):
        # Prepare and start loading resources

        # MQTT
        client = mqtt.Client()
        client.on_connect = self.on_mqtt_connect
        client.on_message = self.on_mqtt_message
        client.connect('localhost')
        client.loop_start()

        # Timer
        clock = pygame.time.Clock()
        
        start = 0
        flag = True

        while True:
            if self.enable_temperature:
                minutes = datetime.datetime.now().time().minute
            
                if minutes % 2 == 0 and start == 0 and flag:
                    start = time.time()
                    self.source = self.temperature
                
                if start > 0 and time.time() - start > 10:
                    start = 0
                    flag = False
                    self.source = self.clock
                
                if minutes % 2 == 1:
                    flag = True
            
            # Limit CPU usage do not go faster than FPS
            dt = clock.tick(self.source.fps)

            self.source.update(dt)
            
            # Update the display buffer
            self.display.buffer = self.source.buffer

            # Render the frame
            self.display.show()

        return


# Function declarations


def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower():
                return True
    except Exception:
        pass
    return False


# Main body
if __name__ == '__main__':
    wordclock = WordClock()
    wordclock.display.show()

    wordclock.mainloop()
