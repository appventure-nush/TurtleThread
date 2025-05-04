import turtlethread

turtle = turtlethread.Turtle()

with turtle.running_stitch(25):
    turtle.forward(100)

with turtle.triple_stitch(40): # Will look identical, but with different stitch length
    turtle.forward(100)

turtle.visualise()