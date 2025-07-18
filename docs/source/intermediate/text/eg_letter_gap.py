with turtlethread.LetterDrawer(turtle) as ld: 
    ld.load_font('Arial') 

    # with default letter gap scale factor -0.1 
    ld.draw_one_letter('Arial', 'T', 120) 
    ld.draw_letter_gap() 
    ld.draw_one_letter('Arial', 'E', 120) 

    # equivalent of carriage return in typewriters 
    with turtle.jump_stitch(): 
        turtle.goto(0, 0)
    ld.draw_string('Arial', '\n', 120)


    # set default letter gap scale factor to 0.3 
    turtlethread.LetterDrawer.letter_gap = 0.3 
    
    ld.draw_one_letter('Arial', 'T', 120) 
    ld.draw_letter_gap() 
    ld.draw_one_letter('Arial', 'E', 120) 

turtle.visualise() 