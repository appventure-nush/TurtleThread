# to import turtlethread 
import sys 
sys.path.insert(1, "./../src")

from pathlib import Path
savedir = Path(__file__).parent 

import turtlethread 

te = turtlethread.Turtle() 

for color in ['green', 'blue', 'black', 'blue']: 
    te.color(color) 
    with te.running_stitch(9999): 
        te.forward(100) 
    te.right(90) 

te.right(195) 

for color in ['red', 'green', 'red']: 
    te.color(color) 
    with te.running_stitch(9999): 
        te.forward(150) 
        te.right(120) 


print(te.pattern.to_pyembroidery().threadlist) 



te.save(str(savedir / 'test_colour.exp'), str(savedir / 'test_colour.inf')) 
te.save(str(savedir / 'test_colour.png'))
