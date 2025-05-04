import turtlethread 

turtle = turtlethread.Turtle() 
with turtlethread.LetterDrawer(turtle) as ld: 
    # We can use the letter drawer in this indented area 
    ld.load_font('Arial') 
    ld.load_font('Calibri') 
    
    # Draw "TEXT" with different fonts 
    ld.draw_one_letter('Arial', 'T', 120, fill=False, outline=True) 
    ld.draw_letter_gap(120) # We must have a letter_gap if we're using ld.draw_one_letter 
    ld.draw_string('Calibri', 'EX', 120, fills=False, outlines=True) # ld.draw_string handles letter_gaps inside 
    ld.draw_letter_gap(120) 
    ld.draw_one_letter('Arial', 'T', 120, fill=False, outline=True) 
    
    ld.draw_letter_gap(120) 
    ld.draw_string('Arial', ' ', 120) 
    ld.draw_letter_gap(120) 
    
    # Fill types 
    ld.draw_string('Arial', "SAM", 120, fills=True, outlines=False, full_fill=True) # Full fill - best used without outline 
    ld.draw_string("Arial", "PLE", 120, fills=True, outlines=True, full_fill=False) # Prtial fill - best used with outline 

# From here on, this unindented code cannot use LetterDrawer. 
turtle.visualise()