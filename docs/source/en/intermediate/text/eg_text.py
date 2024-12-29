import turtlethread

turtle = turtlethread.Turtle() 
with turtlethread.LetterDrawer(turtle) as ld: 
    # We can use the letter drawer in this indented area 
    # Use LetterDrawer as 'ld' here...
    ld.load_font('Arial') 
    ld.load_font('Calibri') 
    
    ld.draw_one_letter('Arial', 'T', 120) 
    ld.draw_letter_gap(120) 
    ld.draw_string('Calibri', 'EX', 120) 
    ld.draw_letter_gap(120) 
    ld.draw_one_letter('Arial', 'T', 120) 