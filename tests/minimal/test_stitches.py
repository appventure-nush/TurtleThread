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


class TestTurtleJumpStitch:
    def test_turtle_jump_stitch_context(self, turtle):
        # Check that we get a trim command in the beginning
        # TODO: Maybe more?
        with turtle.jump_stitch():
            assert isinstance(turtle._stitch_group_stack[-1], stitches.JumpStitch)
        assert not turtle.pattern.to_pyembroidery().stitches

    def test_turtle_forward(self, turtle):
        """Test ``turtle.forward`` with different angles."""
        with turtle.jump_stitch(skip_intermediate_jumps=False):
            turtle.angle = 0
            turtle.forward(10)

            turtle.angle = 90
            turtle.forward(10)

            turtle.angle = 45
            turtle.forward(10)

            turtle.angle = 45 + 180
            turtle.forward(10)

        assert turtle.pattern.to_pyembroidery().stitches == approx_list(
            [
                [0, 0, TRIM],  # From the jump_stitch context manager. Should this be here?
                [10.0, 0, JUMP],
                [10.0, 10.0, JUMP],
                [10 * (1 + sin(pi / 4)), 10 * (1 + sin(pi / 4)), JUMP],
                [10.0, 10.0, JUMP],
            ]
        )

    def test_turtle_backward(self, turtle):
        """Test ``turtle.backward`` with different angles."""
        with turtle.jump_stitch(skip_intermediate_jumps=False):
            turtle.angle = 0
            turtle.backward(10)

            turtle.angle = 90
            turtle.backward(10)

            turtle.angle = 45
            turtle.backward(10)

            turtle.angle = 45 + 180
            turtle.backward(10)

        assert turtle.pattern.to_pyembroidery().stitches == approx_list(
            [
                [0, 0, TRIM],  # From the jump_stitch context manager.
                [-10.0, 0, JUMP],
                [-10.0, -10.0, JUMP],
                [-10 * (1 + sin(pi / 4)), -10 * (1 + sin(pi / 4)), JUMP],
                [-10.0, -10.0, JUMP],
            ]
        )

    @pytest.mark.parametrize("steps", [1, 2, 5, 10])
    @pytest.mark.parametrize("extent", [30, 90, 180, 360])
    @pytest.mark.parametrize("radius", [0, 1, 5, 10])
    @pytest.mark.parametrize("angle_mode", ["degrees", "radians"])
    @pytest.mark.parametrize("skip_intermediate_jumps", [True, False])
    def test_circle(self, turtle, radius, extent, steps, angle_mode, skip_intermediate_jumps):
        turtle.angle_mode = angle_mode
        with turtle.jump_stitch(skip_intermediate_jumps=skip_intermediate_jumps):
            turtle.angle = 0
            turtle.circle(radius, extent=extent, steps=steps)

        center_x = 0
        center_y = radius
        if skip_intermediate_jumps:
            # Only two stitches (TRIM and JUMP)
            assert len(turtle.pattern.to_pyembroidery().stitches) == 2
        else:
            # One JUMP stitch for every step and an additional TRIM stitch
            assert len(turtle.pattern.to_pyembroidery().stitches) == steps + 1

        for x, y, stitch_type in turtle.pattern.to_pyembroidery().stitches[1:]:
            distance_to_center = sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            assert distance_to_center == approx(radius)
            assert stitch_type == JUMP

    @pytest.mark.parametrize("x", [0, -10, 10])
    @pytest.mark.parametrize("y", [0, -10, 10])
    def test_goto(self, turtle, x, y):
        with turtle.jump_stitch():
            turtle.goto(x, y)

        assert turtle.pattern.to_pyembroidery().stitches == approx_list(
            [
                [0, 0, TRIM],  # From the jump_stitch context manager.
                [x, y, JUMP],
            ]
        )

    @pytest.mark.parametrize("x", [0, -10, 10])
    @pytest.mark.parametrize("y", [0, -10, 10])
    def test_home(self, turtle, x, y):
        with turtle.jump_stitch(skip_intermediate_jumps=False):
            turtle.goto(x, y)
            turtle.home()

        assert turtle.pattern.to_pyembroidery().stitches == approx_list(
            [
                [0, 0, TRIM],  # From the jump_stitch context manager.
                [x, y, JUMP],
                [0, 0, JUMP],
            ]
        )

    def test_start_jump_stitch_sets_stitch_type(self, turtle):
        turtle.start_jump_stitch()
        assert isinstance(turtle._stitch_group_stack[-1], stitches.JumpStitch)


class TestTurtleRunningStitch:
    @pytest.mark.parametrize("radius", [0, 1, 10])
    @pytest.mark.parametrize("extent", [30, 90, 180, 360])
    @pytest.mark.parametrize("steps", [1, 2, 4, 10])
    @pytest.mark.parametrize("stitch_length", [1, 10, 20])
    @pytest.mark.parametrize("angle_mode", ["degrees", "radians"])
    def test_circle(self, turtle, stitch_length, radius, extent, steps, angle_mode):
        """
        Test that all stitches are inside the circle given by `radius`
        and outside the incircle of the polygon with `steps` sides and
        radius equal `radius`.

        This test only works for extent <= full revolution. Otherwise, we may not create
        a regular polygon with the computed inner radius.
        """
        turtle.angle_mode = angle_mode
        if angle_mode == "radians":
            extent = radians(extent)
        inner_radius = radius * cos(pi / steps)

        with turtle.running_stitch(stitch_length):
            turtle.circle(radius, extent=extent, steps=steps)

        center_x = 0
        center_y = radius
        tol = 10e-8
        for x, y, stitch_type in turtle.pattern.to_pyembroidery().stitches[1:]:
            distance_to_center = sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            assert distance_to_center <= radius + tol
            assert distance_to_center >= inner_radius - tol
            assert stitch_type == STITCH

    @pytest.mark.parametrize("radius", [0, 2, 10, 100])
    @pytest.mark.parametrize("extent", [30, 90, 180, 360])
    @pytest.mark.parametrize("steps", [1, 2, 4, 10])
    @pytest.mark.parametrize("stitch_length", [1, 10, 20, 1000])
    @pytest.mark.parametrize("angle_mode", ["degrees", "radians"])
    def test_circle_subsequent_step_length(self, turtle, stitch_length, radius, extent, steps, angle_mode):
        """
        Test that any subsquent stitches has distance between 0.5*stitch_length and 1.5*stitch_length
        """
        turtle.angle_mode = angle_mode
        with turtle.running_stitch(stitch_length):
            turtle.circle(radius, extent=extent, steps=steps)

        extent = math.radians(extent * turtle._degreesPerAU)
        side_length = 2 * radius * sin(0.5 * extent / steps)
        tol = 1e-8
        pyemb_pattern = turtle.pattern.to_pyembroidery()
        for (x1, y1, st1), (x2, y2, st2) in zip(pyemb_pattern.stitches[1:], pyemb_pattern.stitches[2:]):
            distance = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            assert distance >= min(0.5 * stitch_length, side_length) - tol
            assert distance < 1.5 * stitch_length + tol

    @pytest.mark.parametrize("radius", [50, 100, 200])
    @pytest.mark.parametrize("extent", [30, 90, 180, 360])
    @pytest.mark.parametrize("stitch_length", [1, 5, 10, 20, 30])
    @pytest.mark.parametrize("angle_mode", ["degrees", "radians"])
    def test_circle_subsequent_step_length_when_step_not_given(self, turtle, stitch_length, radius, extent, angle_mode):
        turtle.angle_mode = angle_mode
        with turtle.running_stitch(stitch_length):
            turtle.circle(radius, extent=extent, steps=None)
        n_steps = turtle._steps_from_stitch_length(stitch_length, radius, extent)

        pyemb_pattern = turtle.pattern.to_pyembroidery()
        assert len(pyemb_pattern.stitches) == n_steps + 1
        for (x1, y1, st1), (x2, y2, st2) in zip(pyemb_pattern.stitches[1:], pyemb_pattern.stitches[2:]):
            distance = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            assert distance >= 0.5 * stitch_length
            assert distance < 1.5 * stitch_length

    @pytest.mark.parametrize("radius", [30, 50, 100])
    @pytest.mark.parametrize("extent", [30, 90, 180, 360])
    @pytest.mark.parametrize("stitch_length", [1, 2, 10])
    def test_n_sides_from_side_length(self, turtle, stitch_length, radius, extent):
        steps = turtle._n_sides_from_side_length(stitch_length, radius, radians(extent))
        step_length = 2 * radius * sin(radians(0.5 * extent) / steps)
        assert step_length == approx(stitch_length)

    def test_too_long_stitches_for_steps_calculation(self, turtle):
        with pytest.warns(UserWarning):
            with turtle.running_stitch(100):
                turtle.circle(10, steps=None)
        assert len(turtle.pattern.to_pyembroidery().stitches) == 5

    def test_just_one_step_for_zero_radius(self, turtle):
        with pytest.warns(UserWarning):
            with turtle.running_stitch(5):
                turtle.circle(0, steps=None)
        assert len(turtle.pattern.to_pyembroidery().stitches) == 2

    @pytest.mark.parametrize("stitch_length", [1, 2, 10, 30])
    @pytest.mark.parametrize("step_length", [10, 100, 500])
    def test_forward_different_stitch_lengths(self, turtle, stitch_length, step_length):
        with turtle.running_stitch(stitch_length):
            turtle.forward(step_length)

        stitches = turtle.pattern.to_pyembroidery().stitches
        for (x1, y1, st1), (x2, y2, st2) in zip(stitches[1:-2], stitches[2:-1]):
            distance = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            assert st1 == st2 == STITCH
            assert distance == approx(stitch_length)

        x1, y1, st1 = stitches[-2]
        x2, y2, st2 = stitches[-1]
        assert st1 == st2 == STITCH
        final_distance = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        if step_length >= 0.5 * stitch_length:
            assert final_distance >= 0.5 * stitch_length
            assert final_distance < 1.5 * stitch_length
        else:
            assert final_distance == approx(step_length)

    @pytest.mark.parametrize("stitch_length", [1, 2, 10, 30])
    @pytest.mark.parametrize("step_length", [10, 100, 500])
    def test_backward_different_stitch_lengths(self, turtle, stitch_length, step_length):
        with turtle.running_stitch(stitch_length):
            turtle.backward(step_length)

        stitches = turtle.pattern.to_pyembroidery().stitches
        for (x1, y1, st1), (x2, y2, st2) in zip(stitches[1:-2], stitches[2:-1]):
            distance = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            assert st1 == st2 == STITCH
            assert distance == approx(stitch_length)

        x1, y1, st1 = stitches[-2]
        x2, y2, st2 = stitches[-1]
        assert st1 == st2 == STITCH
        final_distance = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        if step_length >= 0.5 * stitch_length:
            assert final_distance >= 0.5 * stitch_length
            assert final_distance < 1.5 * stitch_length
        else:
            assert final_distance == approx(step_length)

    def test_start_running_stitch_sets_stitch_type(self, turtle):
        turtle.start_running_stitch(10)
        assert isinstance(turtle._stitch_group_stack[-1], stitches.RunningStitch)


class TestTurtleTripleStitch:
    @pytest.mark.parametrize("stitch_length", [2, 5, 10, 20, 50, 100])
    @pytest.mark.parametrize("step_scaling_factor", [0.1, 0.5, 1])
    def test_forward_single_step(self, turtle, stitch_length, step_scaling_factor):
        with turtle.triple_stitch(stitch_length):
            turtle.forward(stitch_length * step_scaling_factor)

        stitches = turtle.pattern.to_pyembroidery().stitches
        assert len(stitches) == 4
        assert stitches[0] == (0, 0, STITCH)
        assert stitches[1] == (stitch_length * step_scaling_factor, 0, STITCH)
        assert stitches[2] == stitches[0]
        assert stitches[3] == stitches[1]

    @pytest.mark.parametrize("stitch_length", [2, 5, 10, 20, 50, 100])
    def test_forward_two_steps(self, turtle, stitch_length):
        with turtle.triple_stitch(stitch_length):
            turtle.forward(2 * stitch_length)

        stitches = turtle.pattern.to_pyembroidery().stitches
        assert len(stitches) == 7
        assert stitches[0] == (0, 0, STITCH)
        assert stitches[1] == (stitch_length, 0, STITCH)
        assert stitches[2] == stitches[0]
        assert stitches[3] == stitches[1]
        assert stitches[4] == (stitch_length * 2, 0, STITCH)
        assert stitches[5] == stitches[3]
        assert stitches[6] == stitches[4]

    @pytest.mark.parametrize("stitch_length", [2, 5, 10, 20, 50, 100])
    def test_forward_single_step_twice(self, turtle, stitch_length):
        with turtle.triple_stitch(stitch_length):
            turtle.forward(stitch_length)
            turtle.forward(stitch_length)

        stitches = turtle.pattern.to_pyembroidery().stitches
        assert len(stitches) == 7
        assert stitches[0] == (0, 0, STITCH)
        assert stitches[1] == (stitch_length, 0, STITCH)
        assert stitches[2] == stitches[0]
        assert stitches[3] == stitches[1]
        assert stitches[4] == (stitch_length * 2, 0, STITCH)
        assert stitches[5] == stitches[3]
        assert stitches[6] == stitches[4]

    @pytest.mark.parametrize("stitch_length", [2, 5, 10, 20, 50, 100])
    @pytest.mark.parametrize("steps", [4, 5, 10])
    def test_circle(self, turtle, stitch_length, steps):
        """We get the correct number of stitches when creating a circle.

        Here, we use a circle with at least 4 steps, i.e. a square. To make sure that each side consists of only one
        stitch, we set the radius to stitch_length, which will give us maximum side lengths of sqrt(2)*stitch_length
        (for 4 steps). Since this is less than 1.5*stitch_length, we only get a single stitch per side of the square.
        """
        with turtle.triple_stitch(stitch_length):
            turtle.circle(stitch_length, steps=steps)

        stitches = turtle.pattern.to_pyembroidery().stitches
        assert len(stitches) == 3 * steps + 1

    def test_start_triple_stitch_sets_stitch_type(self, turtle):
        turtle.start_triple_stitch(10)
        assert isinstance(turtle._stitch_group_stack[-1], stitches.TripleStitch)


class TestTurtleUnitStitch:
    def test_round_stitch_length(self):
        # Notation, let stitch length be S, distance be D
        # Test 1: Test if S == D, so stitch length == D
        assert approx(stitches.UnitStitch.round_stitch_length(20, 20)) == 20
        # Test 2: Test if D < S, so stitch length == D
        assert approx(stitches.UnitStitch.round_stitch_length(20, 10)) == 10
        # Test 3: Test if S is a multiple of D, so stitch length == S
        assert approx(stitches.UnitStitch.round_stitch_length(20, 100)) == 20
        # Test 4: Test if S is not a multiple of D, so S is the closest multiple of D
        assert approx(stitches.UnitStitch.round_stitch_length(30, 100)) == 33.33333333333333


class TestTurtleZigzagStitch:
    def test_zigzag_unit(self):
        zigzag_stitch = stitches.ZigzagStitch(
            start_pos=Vec2D(0, 0), 
            stitch_length=20, 
            stitch_width=10,
            color=None
        )
        commands = list(zigzag_stitch._stitch_unit(Vec2D(0, 0), 0, 20)) 
        assert len(commands) == 2
        assert commands[0] == (approx(10), approx(-10), STITCH)
        assert commands[1] == (approx(20), approx(0), STITCH)

    def test_zigzag_start_unit(self):
        zigzag_stitch = stitches.ZigzagStitch(
            start_pos=Vec2D(0, 0), 
            stitch_length=20, 
            stitch_width=10,
            color=None,
            center=True
        )
        commands = list(zigzag_stitch._start_stitch_unit(Vec2D(0, 0), 0, 20)) 
        assert len(commands) == 1
        assert commands[0] == (approx(5), approx(5), STITCH)

    def test_zigzag_end_unit(self):
        zigzag_stitch = stitches.ZigzagStitch(
            start_pos=Vec2D(0, 0), 
            stitch_length=20, 
            stitch_width=10,
            color=None,
            center=True
        )
        # Test 1: One additional stitch remaining
        commands = list(zigzag_stitch._end_stitch_unit(Vec2D(0, 0), 0, 20, 15)) 
        assert len(commands) == 1
        assert commands[0] == (approx(10), approx(-10), STITCH)
        # Test 2: No additional stitches needed
        commands = list(zigzag_stitch._end_stitch_unit(Vec2D(0, 0), 0, 20, 5)) 
        assert len(commands) == 0

    @pytest.mark.parametrize("start_pos", [Vec2D(0, 0), Vec2D(100, 100), Vec2D(-100, -100)])
    @pytest.mark.parametrize("end_pos", [Vec2D(100, -100), Vec2D(-100, 100)])
    @pytest.mark.parametrize("stitch_length", [10, 25, 30])
    @pytest.mark.parametrize("stitch_width", [3, 10, 25, 30])
    @pytest.mark.parametrize("center", [True, False])
    @pytest.mark.parametrize("auto_adjust", [True, False])
    def test_zigzag_total_distance(self, start_pos, end_pos, stitch_length, stitch_width, center, auto_adjust):
        zigzag_stitch = stitches.ZigzagStitch(
            start_pos=start_pos, 
            stitch_length=stitch_length, 
            stitch_width=stitch_width,
            color=None,
            center=center,
            auto_adjust=auto_adjust,
            enforce_start_stitch=True,
            enforce_end_stitch=True
        )
        zigzag_stitch.add_location(end_pos)
        commands = zigzag_stitch.get_stitch_commands()
        assert commands[0] == (approx(start_pos[0]), approx(start_pos[1]), STITCH)
        assert commands[-1] == (approx(end_pos[0]), approx(end_pos[1]), STITCH)

    def test_start_zigzag_stitch_sets_stitch_type(self, turtle):
        turtle.start_zigzag_stitch(20, 20)
        assert isinstance(turtle._stitch_group_stack[-1], stitches.ZigzagStitch)


class TestTurtleSatinStitch:
    def test_satin_initialization(self):
        satin_stitch = stitches.SatinStitch(
            start_pos=Vec2D(0, 0), 
            stitch_width=10,
            color=None
        )
        assert isinstance(satin_stitch, stitches.SatinStitch)

    @pytest.mark.parametrize("start_pos", [Vec2D(0, 0), Vec2D(100, 100), Vec2D(-100, -100)])
    @pytest.mark.parametrize("end_pos", [Vec2D(100, -100), Vec2D(-100, 100)])
    @pytest.mark.parametrize("stitch_width", [3, 10, 25, 30])
    @pytest.mark.parametrize("center", [True, False])
    def test_satin_total_distance(self, start_pos, end_pos, stitch_width, center):
        satin_stitch = stitches.SatinStitch(
            start_pos=start_pos, 
            stitch_width=stitch_width,
            color=None,
            center=center
        )
        satin_stitch.add_location(end_pos)
        commands = satin_stitch.get_stitch_commands()
        assert commands[0] == (approx(start_pos[0]), approx(start_pos[1]), STITCH)
        assert commands[-1] == (approx(end_pos[0]), approx(end_pos[1]), STITCH)

    def test_start_satin_stitch_sets_stitch_type(self, turtle):
        turtle.start_satin_stitch(20)
        assert isinstance(turtle._stitch_group_stack[-1], stitches.SatinStitch)

class TestTurtleCrossStitch:
    def test_cross_unit(self):
        cross_stitch = stitches.CrossStitch(
            start_pos=Vec2D(0, 0), 
            stitch_length=20, 
            stitch_width=10,
            color=None
        )
        commands = list(cross_stitch._stitch_unit(Vec2D(0, 0), 0, 20)) 
        assert len(commands) == 3
        assert commands[0] == (20, -10, STITCH)
        assert commands[1] == (0, -10, STITCH)
        assert commands[2] == (20, 0, STITCH) 

    def test_cross_start_unit(self):
        cross_stitch = stitches.CrossStitch(
            start_pos=Vec2D(0, 0), 
            stitch_length=20, 
            stitch_width=10,
            color=None,
            center=True
        )
        commands = list(cross_stitch._start_stitch_unit(Vec2D(0, 0), 0, 20)) 
        assert len(commands) == 1
        assert commands[0] == (approx(0), approx(5), STITCH)

    def test_cross_end_unit(self):
        cross_stitch = stitches.CrossStitch(
            start_pos=Vec2D(0, 0), 
            stitch_length=20, 
            stitch_width=10,
            center=True,
            color=None
        )
        commands = list(cross_stitch._end_stitch_unit(Vec2D(0, 0), 0, 20, 0)) 
        assert len(commands) == 1
        assert commands[0] == (approx(0), approx(-5), STITCH)

    @pytest.mark.parametrize("start_pos", [Vec2D(0, 0), Vec2D(100, 100), Vec2D(-100, -100)])
    @pytest.mark.parametrize("end_pos", [Vec2D(100, -100), Vec2D(-100, 100)])
    @pytest.mark.parametrize("stitch_length", [10, 25, 30])
    @pytest.mark.parametrize("stitch_width", [3, 10, 25, 30])
    @pytest.mark.parametrize("center", [True, False])
    @pytest.mark.parametrize("auto_adjust", [True, False])
    def test_cross_total_distance(self, start_pos, end_pos, stitch_length, stitch_width, center, auto_adjust):
        cross_stitch = stitches.CrossStitch(
            start_pos=start_pos, 
            stitch_length=stitch_length, 
            stitch_width=stitch_width,
            center=center,
            auto_adjust=auto_adjust,
            enforce_start_stitch=True,
            enforce_end_stitch=True,
            color=None
        )
        cross_stitch.add_location(end_pos)
        commands = cross_stitch.get_stitch_commands()
        assert commands[0] == (approx(start_pos[0]), approx(start_pos[1]), STITCH)
        assert commands[-1] == (approx(end_pos[0]), approx(end_pos[1]), STITCH)

    def test_start_cross_stitch_sets_stitch_type(self, turtle):
        turtle.start_cross_stitch(20, 20)
        assert isinstance(turtle._stitch_group_stack[-1], stitches.CrossStitch)


class TestTurtleZStitch:
    def test_z_unit(self):
        z_stitch = stitches.ZStitch(
            start_pos=Vec2D(0, 0), 
            stitch_length=20, 
            stitch_width=10,
            color=None
        )
        commands = list(z_stitch._stitch_unit(Vec2D(0, 0), 0, 20)) 
        assert len(commands) == 2
        assert commands[0] == (approx(20), approx(-10), STITCH)
        assert commands[1] == (approx(20), approx(0), STITCH)

    def test_z_start_unit(self):
        z_stitch = stitches.ZStitch(
            start_pos=Vec2D(0, 0), 
            stitch_length=20, 
            stitch_width=10,
            center=True,
            color=None
        )
        commands = list(z_stitch._start_stitch_unit(Vec2D(0, 0), 0, 20)) 
        assert len(commands) == 2
        assert commands[0] == (approx(10), approx(-5), STITCH)
        assert commands[1] == (approx(10), approx(5), STITCH)

    def test_z_end_unit(self):
        z_stitch = stitches.ZStitch(
            start_pos=Vec2D(0, 0), 
            stitch_length=20, 
            stitch_width=10,
            center=True,
            color=None
        )
        commands = list(z_stitch._end_stitch_unit(Vec2D(0, 0), 0, 20, 0)) 
        assert len(commands) == 0

    @pytest.mark.parametrize("start_pos", [Vec2D(0, 0), Vec2D(100, 100), Vec2D(-100, -100)])
    @pytest.mark.parametrize("end_pos", [Vec2D(100, -100), Vec2D(-100, 100)])
    @pytest.mark.parametrize("stitch_length", [10, 25, 30])
    @pytest.mark.parametrize("stitch_width", [3, 10, 25, 30])
    @pytest.mark.parametrize("center", [True, False])
    @pytest.mark.parametrize("auto_adjust", [True, False])
    def test_z_total_distance(self, start_pos, end_pos, stitch_length, stitch_width, center, auto_adjust):
        z_stitch = stitches.ZStitch(
            start_pos=start_pos, 
            stitch_length=stitch_length, 
            stitch_width=stitch_width,
            center=center,
            auto_adjust=auto_adjust,
            enforce_start_stitch=True,
            enforce_end_stitch=True,
            color=None
        )
        z_stitch.add_location(end_pos)
        commands = z_stitch.get_stitch_commands()
        assert commands[0] == (approx(start_pos[0]), approx(start_pos[1]), STITCH)
        assert commands[-1] == (approx(end_pos[0]), approx(end_pos[1]), STITCH)

    def test_start_z_stitch_sets_stitch_type(self, turtle):
        turtle.start_z_stitch(20, 20)
        assert isinstance(turtle._stitch_group_stack[-1], stitches.ZStitch)

