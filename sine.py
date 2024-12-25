from math import pi, tau, sin, cos
from tree import *

STEPS = 72
FILENAME = "sine.json"

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

tree = Tree()
state = State(modulus=36)

shaders = [make_wave_shader(tree, color=0x901eff, freq=2, amp=600)]
tree.generate(FILENAME, state, shaders, 0x0)