from turtlethread import Turtle

turtle = Turtle() # Use the TurtleThread Turtle

turtle.start_running_stitch(25)
turtle.forward(100)
turtle.cleanup_stitch_type() # Always clean up before using another stitch type!

turtle.visualise() # Required for a visual output!