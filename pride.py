from tree import *

FILENAME = "pride.json"

tree = Tree()
state = State(modulus=36)

def make_layer_shader(tree, color, thickness, zoffset):
    def shader(state):
        rate = tree.zrange / state.modulus
        z = tree.minz + (zoffset + rate * state.serial) % tree.zrange
        return tree.light_close(color, z=z, dz=thickness / 2, dim_func=one)
    return shader

shaders = [make_layer_shader(tree, 0x297382, 275, 0),
           make_layer_shader(tree, 0x4c00ff, 275, 275),
           make_layer_shader(tree, 0x800026, 275, 550),
           make_layer_shader(tree, 0xedff00, 275, 825),
           make_layer_shader(tree, 0x8cff00, 275, 1100),
           make_layer_shader(tree, 0x03e403, 275, 1375)]
tree.generate(FILENAME, state, shaders, 0)