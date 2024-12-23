from manim import *
from manim.opengl import *


class IntroScene(ThreeDScene):
    def construct(self):
        cone = Cone(base_radius=1, height=7, fill_color=GREEN, direction=Z_AXIS).shift(7*Z_AXIS)
        axes = ThreeDAxes()
        sphere = Sphere(radius=0.25, fill_color=RED)
        self.set_camera_orientation(phi=PI / 2)
        self.camera.shift(-1*Y_AXIS + 3*Z_AXIS)
        self.add(axes, cone, sphere)

        # this is new!
        self.interactive_embed()
