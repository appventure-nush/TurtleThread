from pathlib import Path
savedir = Path(__file__).parent / "text" / "exps" 

# to import turtlethread 
import sys 
sys.path.insert(1, "./../src")

import turtlethread 


'''
# draw_one_letter demo 
print("draw_one_letter demo")
te = turtlethread.Turtle() 
with turtlethread.LetterDrawer(te) as ld: 
    ld.load_font('Arial') 
    ld.load_font('Calibri')

    ld.draw_one_letter('Arial', 'T', 120) 

te.save(str(savedir / "draw_one_letter.exp")) 
te.visualise() 



# draw_letter_gap demos 
print('draw_letter_gap demos')

te = turtlethread.Turtle() 
with turtlethread.LetterDrawer(te) as ld: 
    ld.load_font('Arial') 
    ld.load_font('Calibri')
    
    ld.draw_one_letter('Arial', 'T', 120) 
    ld.draw_letter_gap(120) 
    ld.draw_one_letter('Arial', 'E', 120) 

te.save(str(savedir / "draw_letter_gap_003.exp")) 
te.visualise() 



te = turtlethread.Turtle() 
with turtlethread.LetterDrawer(te) as ld: 
    ld.load_font('Arial') 
    ld.load_font('Calibri')
    
    turtlethread.LetterDrawer.letter_gap = 0.1 
    
    ld.draw_one_letter('Arial', 'T', 120) 
    ld.draw_letter_gap(120) 
    ld.draw_one_letter('Arial', 'E', 120) 

te.save(str(savedir / "draw_letter_gap_01.exp")) 
te.visualise() 
turtlethread.LetterDrawer.letter_gap = 0.03 





# draw_string demo 
print('draw_string demo')

te = turtlethread.Turtle() 
with turtlethread.LetterDrawer(te) as ld: 
    ld.load_font('Arial') 
    ld.load_font('Calibri')
    
    ld.draw_one_letter('Arial', 'T', 120) 
    ld.draw_letter_gap(120) 
    ld.draw_string('Calibri', 'EX', 120) 
    ld.draw_letter_gap(120) 
    ld.draw_one_letter('Arial', 'T', 120) 

te.save(str(savedir / "draw_string.exp")) 
te.visualise() 




# outlining text demo 
print("outlining text demo")

te = turtlethread.Turtle() 
with turtlethread.LetterDrawer(te) as ld: 
    ld.load_font('Calibri')
    
    ld.draw_string('Calibri', 'Hi', 120, outlines=True) # for draw_string, it's "outlines" not "outline". More details found under "Full text functionalities"

te.save(str(savedir / "outline_text.exp")) 
te.visualise() 




# fill text 
print("fill text")
te = turtlethread.Turtle() 
with turtlethread.LetterDrawer(te) as ld: 
    ld.load_font('Arial') 
    
    ld.draw_one_letter('Arial', 'B', 120, outline=True, fill=False) # no fill 
    ld.draw_letter_gap(120) 
    ld.draw_one_letter('Arial', 'y', 120, outline=True, fill=True, full_fill=False) # partial fill 
    ld.draw_letter_gap(120) 
    ld.draw_one_letter('Arial', 'e', 120, outline=False, fill=True, full_fill=True) # full fill 

#te.save(str(savedir / "fill_text.exp")) 
te.visualise() 
'''


# TL;DR/example 
te = turtlethread.Turtle() 
with turtlethread.LetterDrawer(te) as ld: 
    # we can use the letter drawer in this indented area 
    ld.load_font('Arial') 
    ld.load_font('Calibri') 
    
    # draw "TEXT" with different fonts 
    ld.draw_one_letter('Arial', 'T', 120, fill=False, outline=True) 
    ld.draw_letter_gap(120) # we must have a letter_gap if we're using ld.draw_one_letter 
    ld.draw_string('Calibri', 'EX', 120, fills=False, outlines=True) # ld.draw_string handles letter_gaps inside 
    ld.draw_letter_gap(120) 
    ld.draw_one_letter('Arial', 'T', 120, fill=False, outline=True) 
    
    ld.draw_letter_gap(120) 
    ld.draw_string('Arial', ' ', 120) 
    ld.draw_letter_gap(120) 
    
    # fill types 
    ld.draw_string('Arial', "SAM", 120, fills=True, outlines=False, full_fill=True) # full fill - best used without outline 
    ld.draw_string("Arial", "PLE", 120, fills=True, outlines=True, full_fill=False) # partial fill - best used with outline 

te.save(str(savedir / "example.exp")) 


# visualize at small scale to see it fully 
import turtle
turtle.screensize(3000, 3000)
te.visualise(scale=0.5) 

