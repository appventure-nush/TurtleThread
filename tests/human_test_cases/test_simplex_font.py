import sys 
sys.path.insert(1, "./../src")
import turtlethread 

t = turtlethread.Turtle() 
t.goto(-200, -50)

#sld = turtlethread.SimplexLetterDrawer(t) # can set triple_stitch_length, as this uses triple stitch 
sld = turtlethread.SimplexLetterDrawer(t, bold=True, scale=7, newline_gap=40) 
sld.draw_string("hello\nworld") 

t.visualise(skip=True, check_density=False) 
