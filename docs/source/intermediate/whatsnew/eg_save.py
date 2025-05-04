from turtlethread import Turtle

turtle = Turtle()

with turtle.running_stitch(25):
    for i in range(3):
        turtle.forward(100)
        turtle.right(120)

turtle.visualise() # Check through the visualisation. You may omit this if you know what you are doing to save time.
turtle.save("triangle.exp") # Replace 'triangle.exp' with any file name and file format.