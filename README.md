# WS2811 LED Stuff

Inspired by [this video](https://www.youtube.com/watch?v=TvlpIojusBE) by [Matt Parker](https://standupmaths.com/) I decided I too wanted to decorate a Christmas tree with addressable LEDs and create interesting displays for it using code. So I did, and this is the code I used. The code is not really intended for public consumption but if you can get some use out of it knock yourself out. No real documentation either, except for the sketchy notes below. If it ever gets to a point of general usefulness I'll add more.

## Entry Points / Workflow

* `raspberrypi/server.py`: Runs on the Pi and presents a rudimentary REST interface so I can turn LEDs on and off remotely.
* `scan.py`: Sequentially turns on lights using the REST interface and captures an image from the webcam, then uses CV2 to process and identify the brightest pixel to find the coordinates of the LED. Needs to be run with the tree rotated 0, 90, 180, and 270 degrees to get a complete mapping.
* `cook.py`: Postprocesses the json files generated by `scan.py`. Consolidates and averages the coordinate data from the different views and augments x and y with polar coordinates. Missing LED data is interpolated in r, θ, z space.
* `tree.py`: A class for representing a Christmas tree based on the output data provided by `cook.py`. There are supporting methods and classes for generating animations based on the positions of the LEDs. The Pi I am using is an older model so it is necessary to prerender to get more complex animations to play at a reasonable speed.
* `raspberrypi/play.py`: Runs on the Pi to play the generated animations.