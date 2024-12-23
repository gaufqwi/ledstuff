from math import sin, cos, radians
from random import seed, gauss

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

levels = 15
bare = 0.5
height = 7
radius = 2
nlights = 48
dnlights = 2

dh = (height - bare) / (levels - 1)

def rfun(h):
    return radius - radius * h / height

seed()
points = []
for l in range(levels):
    h = l * dh
    dangle = 360 / (nlights - 1)
    for i in range(nlights):
        a = radians(i * dangle + gauss(0, 3))
        r = rfun(h) + gauss(0, 1 / 12)
        points.append((r * cos(a), r * sin(a), h + i * dh / nlights +  gauss(0, 2 / 12)))
    nlights -= dnlights
    if nlights <= 0:
        break
points = points[:500]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_axis_off()

print(len(points))
x, y, z = zip(*[p for p in points if  3.5 < p[2] < 4 ])
ax.scatter(x, y, z, c='green', marker='.')
x, y, z = zip(*[p for p in points if not (3.5 < p[2] < 4)])
ax.scatter(x, y, z, c='red', marker='.')
plt.show()