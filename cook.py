import json
from argparse import ArgumentParser
from math import hypot, atan2, sin, cos

parser = ArgumentParser()
parser.add_argument("files", nargs="+")
parser.add_argument("-d", "--dest", default="led-map.json")

args = parser.parse_args()

data = []
for f in args.files:
    try:
        with open(f) as datafile:
            data += json.load(datafile)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pass

leds = {}
xtotal = 0
xcount = 0
ytotal = 0
ycount = 0
ztotal = 0
zcount = 0
zmin = 1e6

for datum in data:
    ledcounts = leds.setdefault(datum["pos"], {"pos": datum["pos"], "xt": 0, "yt": 0, "zt": 0, "xc": 0, "yc": 0, "zc": 0, "xs": [], "ys": [], "zs": []})
    ztotal += datum["z"]
    zmin = min(zmin, datum["z"])
    zcount += 1
    ledcounts["zt"] += datum["z"]
    ledcounts["zc"] += 1
    ledcounts["zs"].append(datum["z"])
    try:
        xtotal += datum["x"]
        xcount += 1
        ledcounts["xt"] += datum["x"]
        ledcounts["xc"] += 1
        ledcounts["xs"].append(datum["x"])
    except KeyError:
        pass
    try:
        ytotal += datum["y"]
        ycount += 1
        ledcounts["yt"] += datum["y"]
        ledcounts["yc"] += 1
        ledcounts["ys"].append(datum["y"])
    except KeyError:
        pass

xavg = xtotal / xcount
yavg = ytotal / ycount
for led in leds.values():
    # if led["xc"] > 1 or led["yc"] > 1:
    #     print(led["pos"], led["xs"], led["ys"])
    led["z"] = led["zt"] / led["zc"] - zmin
    if led["xc"] > 0:
        led["x"] = led["xt"] / led["xc"] - xavg
    if led["yc"] > 0:
        led["y"] = led["yt"] / led["yc"] - yavg
    if "x" in led and "y" in led:
        led["a"] = atan2(led["y"], led["x"])
        led["r"] = hypot(led["x"], led["y"])
        led["finished"] = True
        #print((led["x"], led["y"], led["z"]))
    else:
        led["finished"] = False

# Add totally missing leds
for k in set(range(500)).difference(leds.keys()):
    leds[k] = {"finished": False}

finished = [k for k, v in leds.items() if v["finished"]]
finished.sort()
for i in range(len(finished) - 1):
    spos = finished[i]
    epos = finished[i+1]
    start = leds[spos]
    end = leds[epos]
    dpos = epos - spos
    da = (end["a"] - start["a"]) / dpos
    dr = (end["r"] - start["r"]) / dpos
    dz = (end["z"] - start["z"]) / dpos
    a = start["a"]
    r = start["r"]
    z = start["z"]
    for pos in range(spos+1, epos):
        a += da
        r += dr
        z += dz
        if "x" not in leds[pos]:
            leds[pos]["x"] = r * cos(a)
        if "y" not in leds[pos]:
            leds[pos]["y"] = r * sin(a)
        if "z" not in leds[pos]:
            leds[pos]["z"] = z
        leds[pos]["finished"] = True
        leds[pos]["a"] = atan2(leds[pos]["y"], leds[pos]["x"])
        leds[pos]["r"] = hypot(leds[pos]["x"], leds[pos]["y"])

# for led in leds.values():
#     print((led["x"], led["y"], led["z"]))

ledmap = {k: {"x": v["x"], "y": v["y"], "z": v["z"], "a": v["a"], "r": v["r"]} for k, v in leds.items()}

with open(args.dest, "w") as outfile:
    json.dump(ledmap, outfile, indent=2)