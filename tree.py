import json
from math import pi, tau, sqrt, exp

def pack_rgb(r, g, b):
    return (r << 16) | (g << 8) | b

def unpack_rgb(c):
    return (c >> 16) & 0xff, (c >> 8) & 0xff, c & 0xff

def gamma_avg(*colors):
    rt, gt, bt = 0, 0, 0
    for c in colors:
        r, g, b = unpack_rgb(c)
        rt += r * r
        gt += g * g
        bt += b * b
    l = len(colors)
    return pack_rgb(int(sqrt(rt / l)), int(sqrt(gt / l)), int(sqrt(bt / l)))

def make_logistic(slope, inflection):
    def logistic(x):
        return 1 / (1 + exp(-slope * (x - inflection)))
    return logistic
def one(_):
    return 1
class Tree:
    def __init__(self, datafile="led-map.json"):
        with open(datafile) as ledmap:
            leds = json.load(ledmap)
        self.leds = {int(k): v for k, v in leds.items()}
        self.n_leds = len(self.leds)
        self.minx = 1e6
        self.maxx = -1e6
        self.miny = 1e6
        self.maxy = -1e6
        self.minz = 1e6
        self.maxz = -1e6
        self.minr = 1e6
        self.maxr = -1e6
        for led in self.leds.values():
            self.minx, self.maxx = min(self.minx, led["x"]), max(self.maxx, led["x"])
            self.miny, self.maxy = min(self.miny, led["y"]), max(self.maxy, led["y"])
            self.minz, self.maxz = min(self.minz, led["z"]), max(self.maxz, led["z"])
            self.minr, self.maxr = min(self.minr, led["r"]), max(self.maxr, led["r"])
        self.xrange = self.maxx - self.minx
        self.yrange = self.maxy - self.miny
        self.zrange = self.maxz - self.minz
        self.rrange = self.maxr - self.minr

    def find_close(self, **query):
        out = []
        for pos, led in self.leds.items():
            keep = True
            for coord, delta in [("x", "dx"), ("y", "dy"), ("z", "dz"), ("r", "dr")]:
                if coord in query and abs(led[coord] - query[coord]) > query[delta]:
                    keep = False
                    break
            if not keep:
                continue
            if "a" in query and abs((led["a"] - query["a"] + pi) % tau - pi) > query["da"]:
                continue
            out.append(int(pos))
        return out

    def light_close(self, color, dim_func=lambda x: x, gamma=1, **query):
        r, g, b = unpack_rgb(color)
        out = {}
        for pos, led in self.leds.items():
            rdeltas_sq = []
            keep = True
            for coord, delta in [("x", "dx"), ("y", "dy"), ("z", "dz"), ("r", "dr")]:
                if coord in query:
                    rdelta = abs(led[coord] - query[coord]) / query[delta]
                    if rdelta <= 1:
                        rdeltas_sq.append(rdelta * rdelta)
                    else:
                        keep = False
                        break
            if not keep:
                continue
            if "a" in query:
                rdelta = abs((led["a"] - query["a"] + pi) % tau - pi) / query["da"]
                if rdelta > 1:
                    continue
                else:
                    rdeltas_sq.append(rdelta * rdelta)
            factor = sum(rdeltas_sq) / len(rdeltas_sq)
            factor = dim_func(factor)
            factor = factor ** gamma
            out[pos] = pack_rgb(int(factor * r), int(factor * g), int(factor * b))
        return out

    def render(self, state, shaders=[], background=0, agg_func=gamma_avg):
        start = state
        frames = []
        while True:
            frame = []
            components = []
            for shader in shaders:
                components.append(shader(state))
            for pos in range(self.n_leds):
                values = []
                for component in components:
                    try:
                        values.append(component[pos])
                    except KeyError:
                        pass
                if len(values):
                    frame.append(agg_func(*values))
                else:
                    frame.append(background)
            frames.append(frame)
            state = state.next()
            if state.finished() or state == start:
                break
        return frames

    def compress(self, frames, loop=True):
        compressed = []
        frame = []
        for pos in range(self.n_leds):
            frame.append((pos, frames[0][pos]))
        compressed.append(frame)
        n_frames = len(frames)
        for frame_num in range(1, n_frames + 1 if loop else n_frames):
            frame_num = frame_num % n_frames
            frame = []
            for pos in range(self.n_leds):
                if frames[frame_num][pos] != frames[frame_num - 1][pos]:
                    frame.append((pos, frames[frame_num][pos]))
            compressed.append(frame)
        return compressed

    def generate(self, filename, state, shaders=[], background=0, agg_func=gamma_avg, loop=True):
        frames = self.render(state, shaders, background, agg_func)
        frames = self.compress(frames, loop)
        with open(filename, "w") as outfile:
            json.dump(frames, outfile)

class State:
    def __init__(self, serial=0, modulus=1e9, limit=None):
        self.serial = serial
        self.modulus = modulus
        self.limit = limit

    def __eq__(self, other):
        return self.modulus == other.modulus and (self.serial - other.serial) % self.modulus == 0

    def step(self):
        return self.serial % self.modulus

    def finished(self):
        return self.limit and self.serial == self.limit

    def next(self):
        return State(self.serial+1, self.modulus, self.limit)

def make_layer_shader(tree, color, thickness, zoffset):
    def shader(state):
        rate = tree.zrange / state.modulus
        z = tree.minz + (zoffset + rate * state.serial) % tree.zrange
        return tree.light_close(color, z=z, dz=thickness / 2, dim_func=make_logistic(10, 0.5))
    return shader

def make_xlayer_shader(tree, color, thickness, xoffset):
    def shader(state):
        rate = tree.xrange / state.modulus
        x = tree.minx + (xoffset + rate * state.serial) % tree.xrange
        return tree.light_close(color, x=x, dx=thickness / 2)
    return shader

if __name__ == "__main__":
    tree = Tree()
    s = State(modulus=36)
    shaders = [make_layer_shader(tree, 0x0000ff, 200, 0),
               make_layer_shader(tree, 0x00ffff, 200, 200),
               make_layer_shader(tree, 0x00ff00, 200, 400),
               make_layer_shader(tree, 0xffff00, 200, 600),
               make_layer_shader(tree, 0xff0000, 200, 800),
               make_layer_shader(tree, 0xff00ff, 200, 1000),
               make_layer_shader(tree, 0xffffff, 200, 1200)]
    xshaders = [make_xlayer_shader(tree, 0x00ff00, 300, 0),
                make_xlayer_shader(tree, 0xffffff, 300, 300),
                make_xlayer_shader(tree, 0x0000ff, 300, 600)]
    frames = tree.render(s, xshaders)
    compressed = tree.compress(frames)
    with open("xlayers.json", "w") as layers:
        json.dump(compressed, layers, indent=2)