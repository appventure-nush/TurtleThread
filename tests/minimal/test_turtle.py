import math
from math import copysign, cos, degrees, pi, radians, sin, sqrt

import pytest
from pyembroidery import JUMP, STITCH, TRIM
from pytest import approx

import turtlethread.stitches as stitches
from turtlethread import Turtle
from turtlethread.base_turtle import Vec2D


@pytest.fixture
def turtle():
    return Turtle(angle_mode="degrees")


def approx_list(nested_list):
    for element in nested_list:
        if type(element) == list:
            return [approx_list(el) for el in nested_list]
        else:
            return approx(nested_list)

# From original TurtleThread library
class TestTurtle:
    @pytest.mark.parametrize("angle", [0, -10, 10])
    @pytest.mark.parametrize("angle_mode", ["degrees", "radians"])
    def test_angle_property_set(self, turtle, angle, angle_mode):
        turtle.angle_mode = angle_mode
        turtle.angle = angle
        assert turtle.angle == pytest.approx(angle % turtle._fullcircle)

    @pytest.mark.parametrize("angle", [0, -10, 10])
    def test_angle_property_correct_switch_degrees_radians(self, turtle, angle):
        turtle.angle_mode = "degrees"
        turtle.angle = angle
        turtle.angle_mode = "radians"
        assert turtle.angle == radians(angle % 360)

    @pytest.mark.parametrize("angle", [0, -pi / 4, pi])
    def test_angle_property_correct_switch_radians_degrees(self, turtle, angle):
        turtle.angle_mode = "radians"
        turtle.angle = angle
        turtle.angle_mode = "degrees"
        assert turtle.angle == degrees(angle) % 360

    @pytest.mark.parametrize("angle", [0, -10, 10])
    def test_heading_same_as_angle(self, turtle, angle):
        turtle.setheading(angle)
        assert turtle.heading() == turtle.angle
        assert turtle.angle == angle % 360

    @pytest.mark.parametrize("invalid_input", [0, 0.0, [0], float("nan"), float("inf")])
    def test_angle_mode_fails_for_invalid_input_type(self, turtle, invalid_input):
        with pytest.raises(TypeError):
            turtle.angle_mode = invalid_input

    def test_angle_mode_fails_for_invalid_input_value(self, turtle):
        with pytest.raises(KeyError):
            turtle.angle_mode = "invalid_string_input"

    def test_turtle_left(self, turtle):
        turtle.left(90)
        assert turtle.angle == 270 # WORKAROUND

    def test_turtle_right(self, turtle):
        turtle.right(90)
        assert turtle.angle == 90 # WORKAROUND

    @pytest.mark.parametrize("invalid_radius", [float("inf"), float("-inf"), float("-nan")])
    def test_circle_fails_for_invalid_radius(self, turtle, invalid_radius):
        with pytest.raises(ValueError):
            turtle.circle(invalid_radius)

    def test_circle_warns_for_zero_radius(self, turtle):
        with pytest.warns(UserWarning):
            turtle.circle(0)

    def test_home_resets_angle(self, turtle):
        turtle.angle = 3
        turtle.home()
        assert turtle.angle == 0

    def test_home_resets_position(self, turtle):
        turtle.goto(20, 20)
        turtle.home()
        assert turtle.x == 0
        assert turtle.y == 0

    @pytest.mark.parametrize("x", [0, -10, 10])
    @pytest.mark.parametrize("y", [0, -10, 10])
    def test_goto_changes_position(self, turtle, x, y):
        turtle.goto(x, y)
        assert turtle.x == x
        assert turtle.y == y

    @pytest.mark.parametrize("steps", [1, 2, 5, 10])
    @pytest.mark.parametrize("radius", [0, 1, 5, 10])
    @pytest.mark.parametrize("angle_mode", ["degrees", "radians"])
    def test_circle_stops_and_starts_in_same_position(self, turtle, radius, steps, angle_mode):
        turtle.angle_mode = angle_mode
        start_x = turtle.x
        start_y = turtle.y

        turtle.circle(radius=radius, steps=steps)

        assert turtle.x == approx(start_x)
        assert turtle.y == approx(start_y)

    @pytest.mark.parametrize("steps", [1, 2, 5, 10])
    @pytest.mark.parametrize("radius", [-1, 0, 1, 5, 10])
    @pytest.mark.parametrize("angle_mode", ["degrees", "radians"])
    def test_circle_stops_and_starts_with_same_angle(self, turtle, radius, steps, angle_mode):
        turtle.angle_mode = angle_mode
        start_angle = math.radians(turtle.angle * turtle._degreesPerAU)

        turtle.circle(radius=radius, steps=steps)

        end_angle = math.radians(turtle.angle * turtle._degreesPerAU)
        assert end_angle == approx(start_angle)

    def test_circle_considers_radius_sign(self, turtle):
        turtle.angle_mode = "radians"
        turtle.angle = 0
        turtle.circle(radius=100, extent=pi, steps=1)
        assert turtle.x == pytest.approx(0)
        assert turtle.y == pytest.approx(200)
        turtle.home()
        turtle.circle(radius=-100, extent=pi, steps=1)
        assert turtle.x == pytest.approx(0)
        assert turtle.y == pytest.approx(-200)

    def test_use_stitch_group_fails_if_inconsistent_state(self, turtle):
        with pytest.raises(RuntimeError):
            with turtle.running_stitch(20):
                with turtle.running_stitch(20):
                    turtle.cleanup_stitch_type()

    @pytest.mark.parametrize(
        "stitch_group",
        [
            stitches.JumpStitch(Vec2D(0, 0)),
            stitches.RunningStitch(Vec2D(0, 0), None, 20),
            stitches.TripleStitch(Vec2D(0, 0), None, 20),
            stitches.ZigzagStitch(Vec2D(0, 0), None, 20, 20),
            stitches.SatinStitch(Vec2D(0, 0), None, 20),
            stitches.CrossStitch(Vec2D(0, 0), None, 20, 20),
            stitches.ZStitch(Vec2D(0, 0), None, 20, 20),
        ],
    )
    def test_set_stitch_type_sets_stitch_type(self, turtle, stitch_group):
        turtle.set_stitch_type(stitch_group)
        assert turtle._stitch_group_stack[-1] is stitch_group

    def test_nested_stitch_context(self, turtle):
        with turtle.running_stitch(20):
            turtle.forward(20)
            with turtle.running_stitch(10):
                turtle.forward(20)
            turtle.forward(20)

            with turtle.running_stitch(10):
                turtle.forward(20)
                with turtle.running_stitch(5):
                    turtle.forward(10)
            turtle.forward(20)

            with turtle.jump_stitch():
                turtle.forward(50)
                with turtle.running_stitch(10):
                    turtle.forward(20)
                turtle.forward(20)
            turtle.forward(20)

        stitches = turtle.pattern.to_pyembroidery().stitches
        assert stitches == [
            (0, 0, STITCH),  # Parent running stitch group
            (20, 0, STITCH),
            (20, 0, STITCH),  # First nested running stitch group
            (30, 0, STITCH),
            (40, 0, STITCH),
            (40, 0, STITCH),  # Back to parent running  stitch group
            (60, 0, STITCH),
            (60, 0, STITCH),  # Second nested running  stitch group
            (70, 0, STITCH),
            (80, 0, STITCH),
            (80, 0, STITCH),  # Doubly nested running  stitch group
            (85, 0, STITCH),
            (90, 0, STITCH),
            (90, 0, STITCH),  # Back to parent running stitch group
            (110, 0, STITCH),
            (110, 0, TRIM),  # Nested jump stitch
            (160, 0, JUMP),
            (160, 0, STITCH),  # Running stich within nested jump stitch
            (170, 0, STITCH),
            (180, 0, STITCH),
            (180, 0, TRIM),  # Back to jump stitch
            (200, 0, JUMP),
            (200, 0, STITCH),  # Back to parent running stitch
            (220, 0, STITCH),
        ]
