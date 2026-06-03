import turtlethread 

t = turtlethread.Turtle() 
t.goto(-200, -50)

sld = turtlethread.SimplexLetterDrawer(t) 
sld.draw_string("hello\nworld") 

t.visualise() 