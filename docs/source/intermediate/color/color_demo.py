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



te.save('test_color.exp', 'test_color.inf') 
te.save('test_color.png')