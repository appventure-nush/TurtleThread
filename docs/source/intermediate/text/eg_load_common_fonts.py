import turtlethread

turtle = turtlethread.Turtle() 
with turtlethread.LetterDrawer(turtle, load_common_fonts=True) as ld: 
    # 'Arial' will already be loaded!
    # Use LetterDrawer as 'ld' here...
    
    # Draw "TEXT" with different fonts 
    ld.draw_one_letter('Arial', 'T', 120, fill=False, outline=True) 
    ld.draw_letter_gap() # We must have a letter_gap if we're using ld.draw_one_letter 
    ld.draw_string('Calibri', 'EX', 120, fills=False, outlines=True) # ld.draw_string handles letter_gaps inside 
    ld.draw_letter_gap() 
    ld.draw_one_letter('Arial', 'T', 120, fill=False, outline=True) 
    
    ld.draw_letter_gap() 
    ld.draw_string('Arial', ' ', 120) 
    ld.draw_letter_gap() 
    
    # fill types 
    ld.draw_string('Arial', "SAM", 120, fills=True, outlines=False, full_fill=True) # full fill - best used without outline 
    ld.draw_string("Arial", "PLE", 120, fills=True, outlines=True, full_fill=False) # partial fill - best used with outline 
