import turtlethread 

turtle = turtlethread.Turtle() 
with turtlethread.LetterDrawer(turtle) as ld: 
    ld.load_font('Calibri')
    # Note that for ld.draw_string, the parameter is "outlines" and not "outline"!
    # More details can be found in the API reference.
    ld.draw_string('Calibri', 'Hi', 120, outlines=True)