from math import pi, tau
from tree import *

STEP = 10
FILENAME = "candycane.json"

def make_swirl_shader(tree, color, aoffset):
    ma = 1 * tau / (1 * tree.zrange)
    def aofz(z):
        return ma * (z - tree.minz)
    def shader(state):
        out = {}
        basea = aoffset + tau * state.serial / state.modulus
        for z in range(int(tree.minz), int(tree.maxz), STEP):
            a = basea + aofz(z)
            da = tau / 36
            lights = tree.light_close(color, dim_func=one, z=z, dz=20, a=a, da=da)
            out = out | lights
        return out
    return shader

tree = Tree()
state = State(modulus=36)

shaders = [make_swirl_shader(tree, 0x00ff00, 0),
           make_swirl_shader(tree, 0x00ff00, tau / 3),
           make_swirl_shader(tree, 0x00ff00, 2 * tau / 3)]
tree.generate(FILENAME, state, shaders, 0xffffff)