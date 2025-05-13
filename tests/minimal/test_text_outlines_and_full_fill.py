import math
from math import copysign, cos, degrees, pi, radians, sin, sqrt

import pytest
from pytest import approx

from turtlethread import Turtle, LetterDrawer

@pytest.fixture
def turtle():
    return Turtle(angle_mode="degrees")

def test_outline_text(turtle):
    with LetterDrawer(turtle) as ld:
        ld.load_font('Arial')
        ld.draw_one_letter('Arial', 'T', 120, fill=False, outline=True) 
        ld.draw_letter_gap(120)
        ld.draw_string('Arial', 'est', 120, fills=False, outlines=True)
    turtle.visualise(skip=True, done=False, bye=False)

def test_full_fill_text(turtle):
    with LetterDrawer(turtle) as ld:
        ld.load_font('Arial')
        ld.draw_one_letter('Arial', 'T', 120, fill=True, outline=False) 
        ld.draw_letter_gap(120)
        ld.draw_string('Arial', 'est', 120, fills=True, outlines=False)
    turtle.visualise(skip=True, done=False, bye=False)

def test_both_outline_and_full_fill_text(turtle):
    with LetterDrawer(turtle) as ld:
        ld.load_font('Arial')
        ld.draw_one_letter('Arial', 'T', 120, fill=True, outline=True) 
        ld.draw_letter_gap(120)
        ld.draw_string('Arial', 'est', 120, fills=True, outlines=True)
    turtle.visualise(skip=True, done=False, bye=False)