import turtlethread

t = turtlethread.Turtle()

# Simply call the begin_fill() function without any parameters!
t.begin_fill() 

# Draw a triangle
with t.running_stitch(25):
    for i in range(3):
        t.forward(100)
        t.right(120)

# You must call the end_fill() function, or the shape will not be filled!
t.end_fill()

t.fast_visualise(scale=2) # fast_visualise because fills can take a long time 