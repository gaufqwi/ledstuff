import sys
#import board
#import neopixel
import json
from time import sleep

planes = {'x': 0, 'y': 1, 'z': 2}
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

try:
    plane = planes[sys.argv[1]]
except (IndexError, KeyError):
    plane = 0

with open("ledmap.json") as f:
    ledmap = {int(k): v for k, v in json.load(f).items()}

minmax = [1e6, -1e6, 1e6, -1e6, 1e6, -1e6]
for v in ledmap.values():
    for i in range(3):
        minmax[2*i], minmax[2*i+1] = min(minmax[2*i], v[i]), max(minmax[2*i+1], v[i])

def find_near(loc, radius, plane=0):
    points = []
    for i, point in ledmap.items():
        if abs(point[plane] - loc) <= radius:
            points.append(i)
    return points

for i in range(minmax[0], minmax[1], 4):
    print(i, find_near(i, 10, 0))
    sleep(0.5)
