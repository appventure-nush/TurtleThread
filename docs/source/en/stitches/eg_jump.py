import turtlethread

turtle = turtlethread.Turtle()

with turtle.running_stitch(25):
    turtle.forward(100)

with turtle.jump_stitch():
    turtle.right(90)
    turtle.forward(25)
    turtle.right(90)

with turtle.triple_stitch(40):
    turtle.forward(100)

turtle.visualise()