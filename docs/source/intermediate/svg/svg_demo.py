import turtlethread 
te = turtlethread.Turtle() 
from turtlethread.draw_svg import drawSVG 
drawSVG(te, "svg_with_c.svg", 250, 400, fill=False, outline=True)