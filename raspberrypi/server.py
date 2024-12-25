#import board
#import neopixel
from flask import Flask
#import gc
from rpi_ws281x import PixelStrip, Color

# LED strip configuration:
LED_COUNT = 500        # Number of LED pixels.
# LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

#pin = board.D10
#num_pixels = 500

#pixels = neopixel.NeoPixel(pin, num_pixels, auto_write = False, pixel_order = neopixel.RGB)
pixels = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
pixels.begin()

api = Flask(__name__)

last_pixel = -1

flag_colors = [0x00ff00, 0xffffff, 0x0000ff]

@api.route('/white/<int:num>')
def turnonwhite(num):
    global last_pixel
    #pixels.fill(0x0)
    if last_pixel != -1:
        pixels.setPixelColor(last_pixel, 0)
    pixels.setPixelColor(num, 0xffffff)
    last_pixel = num
    pixels.show()
    return f'<p>Turning on light {num}</p>'

@api.route('/red/<int:num>')
def turnonred(num):
    global last_pixel
    #pixels.fill(0x0)
    if last_pixel != -1:
        pixels.setPixelColor(last_pixel, 0)
    pixels.setPixelColor(num, 0x00ff00)
    last_pixel = num
    pixels.show()
    return f'<p>Turning on light {num}</p>'

@api.route('/usa/<int:num>')
def turnonusa(num):
    global last_pixel
    #pixels.fill(0x0)
    if last_pixel != -1:
        pixels.setPixelColor(last_pixel, 0)
    pixels.setPixelColor(num, flag_colors[num % 3])
    last_pixel = num
    pixels.show()
    return f'<p>Turning on light {num}</p>'

@api.route('/off')
def turnoff():
    last_pixel = -1
    for i in range(LED_COUNT):
        pixels.setPixelColor(i, 0)
    pixels.show()
    #gc.collect()
    return f'<p>Turning off all lights</p>'

@api.route('/gc')
def garbage():
    #gc.collect()
    return f'<p>Garbage collected/p>'
    
if __name__ == '__main__':
    try:
        #gc.disable()
        api.run(host='0.0.0.0')
    except KeyboardInterrupt:
        pixels.fill(0x0)
        pixels.show()
    