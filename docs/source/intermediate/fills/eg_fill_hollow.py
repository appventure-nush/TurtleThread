import turtlethread

t = turtlethread.Turtle()

# The close=False argument must be passed for hollow fills!
t.begin_fill(closed=False)

# Draw a large square
with t.running_stitch(25):
    for i in range(4):
        t.forward(200)
        t.left(90)

# Use a jump stitch to 'jump' to the inner part of the filled shape
with t.jump_stitch():
    t.forward(50)
    t.left(90)
    t.forward(50)
    t.right(90)

# Draw the inner square
with t.running_stitch(25):
    for i in range(4):
        t.forward(100)
        t.left(90)

t.end_fill()

t.fast_visualise() # fast_visualise because fills can take a long time 