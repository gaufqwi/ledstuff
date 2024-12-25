from math import pi, tau, sin, cos
from tree import *

FILENAME = "hybrid.json"
STEPS = 72
STEP = 10

tree = Tree()
state = State(modulus=36)

def make_swirl_shader(tree, color, aoffset):
    mr = tree.rrange / tree.zrange
    ma = 1 * tau / (1 * tree.zrange)
    def rofz(z):
        return tree.maxr - mr * (z - tree.minz)
    def aofz(z):
        return ma * (z - tree.minz)
    def shader(state):
        out = {}
        basea = aoffset + tau * state.serial / state.modulus
        for z in range(int(tree.minz), int(tree.maxz), STEP):
            r = rofz(z)
            a = basea + aofz(z)
            da = tau / 36
            #lights = tree.light_close(color, dim_func=one, r=r, a=a, da=da, dr=10)
            lights = tree.light_close(color, dim_func=one, z=z, dz=20, a=a, da=da)
            out = out | lights
        return out
    return shader

def make_wave_shader(tree, color, zoffset=800, amp=400, freq=1, fun=sin):
    step = tau / STEPS
    def shader(state):
        out = {}
        phase = state.serial * tau / state.modulus
        for i in range(STEPS):
            a = i * step
            z = zoffset + amp * fun(freq * a)
            out = out | tree.light_close(color, a=(phase + a), da=tau/36, z=z, dz=50, dim_func=one)
        return out
    return shader

shaders = [make_wave_shader(tree, color=0x901eff, freq=2, amp=600)]
shaders += [make_swirl_shader(tree, 0x00ff00, 0),
            make_swirl_shader(tree, 0x00ff00, tau / 3),
            make_swirl_shader(tree, 0x00ff00, 2 * tau / 3)]
tree.generate(FILENAME, state, shaders, 0)