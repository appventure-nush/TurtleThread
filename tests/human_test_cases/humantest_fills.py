import turtlethread

t = turtlethread.Turtle()

t.begin_fill(closed=False)

with t.direct_stitch():
    for i in range(4):
        t.forward(200)
        t.left(90)

with t.jump_stitch():
    t.forward(50)
    t.left(90)
    t.forward(50)
    t.right(90)

with t.direct_stitch():
    for i in range(4):
        t.forward(100)
        t.left(90)

t.end_fill()

with t.jump_stitch():
    t.goto(0, -100)

with t.direct_stitch():
    t.begin_fill()
    t.circle(50)
    t.end_fill()

t.visualise(skip=True)