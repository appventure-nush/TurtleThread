import turtlethread

turtle = turtlethread.Turtle()

with turtle.zigzag_stitch(25, 25): # By default, the zigzag is not centered!
    turtle.forward(200)

with turtle.jump_stitch():
    turtle.goto(0, 50)

with turtle.zigzag_stitch(25, 50, center=True): # Stitch length of 25, stitch width of 50
    turtle.forward(100)

with turtle.zigzag_stitch(50, 25, center=True): # Stitch length of 50, stitch width of 25
    turtle.forward(100)

turtle.visualise()