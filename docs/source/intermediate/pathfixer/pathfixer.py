orig_turtle = turtlethread.Turtle() 
orig_turtle.color("black")
with orig_turtle.direct_stitch(): 
    for i in range(360*5): 
        orig_turtle.forward(0.8) 
        orig_turtle.right(0.2) 


with orig_turtle.jump_stitch(): 
    orig_turtle.goto(-100, -100)
with turtlethread.LetterDrawer(orig_turtle) as ld: 
    ld.load_font("arial")
    orig_turtle.color("red")
    ld.draw_string("arial", "hi", 30)
    orig_turtle.color("blue")
    ld.draw_string("arial", "he", 30)

orig_turtle.color("green")
turtlethread.SimplexLetterDrawer(orig_turtle, scale=1.5).draw_string("HI2")

orig_turtle.visualise(skip=True, check_density=False, scale=2) 

from turtlethread.fix_path import PathFixer 
new_turtle = PathFixer.fix_path(orig_turtle)
new_turtle.fast_visualise(check_density=False, skip=True, scale=2) 