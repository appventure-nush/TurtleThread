# to import turtlethread 
import sys 
sys.path.insert(1, "./../src")

import turtlethread 
from turtlethread import stitches 

te = turtlethread.Turtle() 
with te.running_stitch(9999): 
    te.forward(100) 

for colour in ['green', 'blue', 'black', 'blue']: 
    te.color(colour) 
    with te.running_stitch(9999): 
        te.forward(100) 

print(te.pattern.to_pyembroidery().threadlist) 
