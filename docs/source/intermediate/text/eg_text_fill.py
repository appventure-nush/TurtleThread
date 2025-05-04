import turtlethread 

turtle = turtlethread.Turtle() 
with turtlethread.LetterDrawer(turtle) as ld: 
    ld.load_font('Arial') 
    
    ld.draw_one_letter('Arial', 'B', 120, outline=True, fill=False) # No fill 
    ld.draw_letter_gap(120) 
    ld.draw_one_letter('Arial', 'y', 120, outline=True, fill=True, full_fill=False) # Partial fill 
    ld.draw_letter_gap(120) 
    ld.draw_one_letter('Arial', 'e', 120, outline=False, fill=True, full_fill=True) # Full fill 