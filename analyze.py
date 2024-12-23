#!/usr/bin/python3

import json

midxy = 366

with open("data.json") as f:
    data = json.load(f)

data_temp = {}
for i in range(50):
    data_temp[i] = {'xt': 0, 'xc': 0, 'yt': 0, 'yc': 0, 'zt': 0, 'zc': 0}

for angle, points in data.items():
    a = int(angle) / 90
    for j, coords in points.items():
        i = int(j)
        xy, z = eval(coords)
        if a > 1:
            xy = 799 - xy
        xy = xy - midxy
        data_temp[i]['zc'] += 1
        data_temp[i]['zt'] += 447 - z
        if (a % 2) == 0:
            data_temp[i]['xc'] += 1
            data_temp[i]['xt'] += xy
        else:
            data_temp[i]['yc'] += 1
            data_temp[i]['yt'] += xy

data_final = {}
for i in range(50):
    data_final[i] = [int(data_temp[i]['xt'] / data_temp[i]['xc']),
                     int(data_temp[i]['yt'] / data_temp[i]['yc']),
                     int(data_temp[i]['zt'] / data_temp[i]['zc'])]

with open("ledmap.json", "w") as ledmap:
    json.dump(data_final, ledmap, indent=2)

