#!/usr/bin/env python3

import argparse

from rpi_ws281x import PixelStrip, Color
import json
from time import sleep
from argparse import ArgumentParser

# LED strip configuration:
LED_COUNT = 500        # Number of LED pixels.
LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


pixels = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
pixels.begin()

class Player:
    def __init__(self):
        self.pixels = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.pixels.begin()

    def load(self, filename):
        with open(filename) as framefile:
            self.frames = json.load(framefile)
            self.framecount = len(self.frames)

    def play(self, delay=0.1):
        loop = self.frames[1:]
        try:
            for pos, color in self.frames[0]:
                pixels[pos] = color
            pixels.show()
            sleep(delay)
            frame = 0
            while True:
                for pos, color in loop[frame]:
                    pixels[pos] = color
                frame = (frame + 1) % (self.framecount - 1)
                pixels.show()
                sleep(delay)
        except KeyboardInterrupt:
            for i in range(LED_COUNT):
                pixels[i] = 0
            pixels.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--delay", type=float, default=0.1)
    args = parser.parse_args()
    player = Player()
    player.load(args.file)
    player.play(args.delay)

