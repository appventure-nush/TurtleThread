import math
import turtlethread
from turtlethread import fills

t = turtlethread.Turtle()

# If the string 'auto' is passed to ScanlineFill, it will automatically try multiple angles and choose the one that
# minimizes the number of jump stitches.
t.begin_fill(fills.ScanlineFill("auto")) 

with t.running_stitch(25):
    for i in range(3):
        t.forward(100)
        t.right(120)

t.end_fill()

# You can also choose an angle (in radians) and pass it to ScanlineFill.
t.begin_fill(fills.ScanlineFill(math.pi/6)) 

# Draw another triangle
t.right(180)
with t.running_stitch(25):
    for i in range(3):
        t.forward(100)
        t.right(120)

t.end_fill()

t.visualise()