import sys 
sys.path.insert(1, "./../src")
import turtlethread 

t = turtlethread.Turtle() 
t.goto(-200, -50)

sld = turtlethread.SimplexLetterDrawer(t) 
sld.draw_string("hello\nworld") 

t.visualise(skip=True, check_density=False) 
