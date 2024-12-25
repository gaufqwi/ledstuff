from tree import *

FILENAME = "french.json"


tree = Tree()
state = State(modulus=36)

def make_xlayer_shader(tree, color, thickness, xoffset):
    def shader(state):
        rate = tree.xrange / state.modulus
        x = tree.minx + (xoffset + rate * state.serial) % tree.xrange
        return tree.light_close(color, x=x, dx=thickness / 2)
    return shader

shaders = [make_xlayer_shader(tree, 0x00ff00, 300, 0),
           make_xlayer_shader(tree, 0xffffff, 300, 300),
           make_xlayer_shader(tree, 0x0000ff, 300, 600)]
tree.generate(FILENAME, state, shaders, 0)