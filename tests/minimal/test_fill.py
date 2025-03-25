import math
from math import copysign, cos, degrees, pi, radians, sin, sqrt

import pytest
from pytest import approx

from turtlethread import Turtle
from turtlethread import fills


@pytest.fixture
def turtle():
    return Turtle(angle_mode="degrees")

def test_fill_defaults(turtle):
    turtle.start_running_stitch(10)
    # Test 1: No parameters
    turtle.begin_fill()
    turtle.circle(50)
    turtle.end_fill()
    turtle.cleanup_stitch_type()
    turtle.visualise(skip=True, done=False, bye=False)

def test_scanlinefill(turtle):
    turtle.start_running_stitch(10)
    # Test 2: ScanlineFill, no parameters
    turtle.begin_fill(fills.ScanlineFill())
    turtle.circle(50)
    turtle.end_fill()
    turtle.visualise(skip=True, done=False, bye=False)
    # Test 3: ScanlineFill, "auto"
    turtle.begin_fill(fills.ScanlineFill(angle="auto"))
    turtle.circle(50)
    turtle.end_fill()
    turtle.visualise(skip=True, done=False, bye=False)
    # Test 4: ScanlineFill, custom angle
    turtle.begin_fill(fills.ScanlineFill(1))
    turtle.circle(50)
    turtle.end_fill()
    turtle.cleanup_stitch_type()
    turtle.visualise(skip=True, done=False, bye=False)

def test_scanlinefill_jump_at_edges(turtle):
    turtle.start_running_stitch(10)
    # Test 5: ScanlineFill, jump at edges
    turtle.begin_fill(fills.ScanlineFill(angle="auto", jump_at_edges=True))
    turtle.circle(50)
    turtle.end_fill()
    turtle.cleanup_stitch_type()
    turtle.visualise(skip=True, done=False, bye=False)

def test_scanlinefill_intersecting_polygons(turtle):
    turtle.begin_fill(closed=False)
    with turtle.direct_stitch(): # Draw outer square
        for i in range(4):
            turtle.forward(200)
            turtle.left(90)
    with turtle.jump_stitch(): # Jump to inner
        turtle.forward(50)
        turtle.left(90)
        turtle.forward(50)
        turtle.right(90)
    with turtle.direct_stitch(): # Draw inner square
        for i in range(4):
            turtle.forward(100)
            turtle.left(90)
    turtle.end_fill() # Fill
    turtle.visualise(skip=True, done=False, bye=False)
    