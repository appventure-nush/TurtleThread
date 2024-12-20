import sys 
sys.path.insert(1, "./../src")
import turtlethread 

pts = [(0,0), 
       (0,100), 
       (20,100), 
       (20, 60), 
       (80, 60), 
       (80, 100), 
       (100, 100), 
       (100, 0), 
       (80, 0), 
       (80, 40), 
       (20, 40), 
       (20, 0), ] 

a = turtlethread.Turtle() 
a.ScanlineFill(90).fill(a, pts) # this bugs out 

a.visualise() 

