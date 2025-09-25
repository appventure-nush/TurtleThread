import os 
from pathlib import Path 
lockdir = Path(__file__).parent 
ttdir = lockdir.parent 



# lock draw svg file -------------------------------------------------------------------------------

with open(ttdir/'draw_svg.py', 'rb') as fin: 
    lines = fin.readlines() 

# add
lock_code = b'''
    # lock usage of this function 
    passed = False 
    caller_frame = inspect.currentframe().f_back 
    while caller_frame: 
        name = caller_frame.f_globals.get("__file__")
        if name.split('\\\\')[-1].strip() in ['text.py', 'svg_demo.py']: 
            passed = True 
            break 
        caller_frame = caller_frame.f_back 
    if not passed: 
        raise ValueError("Cannot use draw SVG features in locked mode!") 
    
    '''

if os.path.exists(lockdir/"locked_draw_svg.py"): 
    os.remove(lockdir/"locked_draw_svg.py") 

with open(lockdir/"locked_draw_svg.py", 'wb') as fout: 
    fout.write(b"import inspect\n\n") 

    i = 0 
    found = False 
    while (not found): 
        line = lines[i] 
        fout.write(line) 
        if (len(line)>11) and line.decode()[:11] == 'def drawSVG': 
            found = True 
        i += 1 

    # add lock code 
    fout.write(lock_code) 

    # write the other lines 
    while (i < len(lines)): 
        fout.write(lines[i]) 
        i += 1 

