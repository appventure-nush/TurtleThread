
# to import turtlethread 
import sys 
sys.path.insert(1, "./../src")

import turtlethread 

te = turtlethread.Turtle() 
with te.running_stitch(10000000): 
    for i in range(20): 
        te.forward(10) 
        te.backward(10) 

te.visualise() # gives density warning 


