import turtlethread 

t = turtlethread.Turtle() 
t.goto(-200, -50)

sld = turtlethread.SimplexLetterDrawer(t, bold=True, scale=7, newline_gap=40) 
sld.draw_string("hello\nworld") 

t.visualise() 