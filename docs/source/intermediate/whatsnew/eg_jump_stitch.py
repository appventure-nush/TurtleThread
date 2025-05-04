from turtlethread import Turtle

turtle = Turtle() # Use the TurtleThread Turtle

with turtle.jump_stitch():
    turtle.forward(100)

# Alternatively, to close follow Turtle syntax...
turtle.start_jump_stitch() # Instead of turtle.penup()
turtle.forward(100)
turtle.cleanup_stitch_type() # Instead of turtle.pendown()

turtle.visualise() # Required for a visual output!