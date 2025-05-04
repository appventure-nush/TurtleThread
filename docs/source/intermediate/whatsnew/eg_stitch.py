from turtlethread import Turtle

turtle = Turtle() # Use the TurtleThread Turtle

with turtle.running_stitch(25):
    turtle.forward(100)

turtle.visualise() # Required for a visual output!