import turtlethread 

turtle = turtlethread.Turtle() 
with turtlethread.LetterDrawer(turtle) as ld: 
    ld.load_font('Arial') 
    turtlethread.LetterDrawer.letter_gap = 0.1 
    
    ld.draw_one_letter('Arial', 'T', 120) 
    ld.draw_letter_gap(120) 
    ld.draw_one_letter('Arial', 'E', 120) 