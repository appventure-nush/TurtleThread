# credits: sewing machine SVG was from svgrepo.com 

from pathlib import Path
savedir = Path(__file__).parent 

# to import turtlethread 
import sys 
sys.path.insert(1, "./../src")

import turtlethread 

te = turtlethread.Turtle() 

from turtlethread.draw_svg import drawSVG 

te.goto(0,0)
drawSVG(te, str(savedir / "svg_with_q.svg"), 250, 400, fill=False, outline=True)


# save 
te.save(str(savedir / "q.exp"))
te.save(str(savedir / "q.png"))

# visualize final product .png with PIL haha 
from PIL import Image 
Image.open(str(savedir / "q.png")).show() 

# visualize 
te.visualise(scale=0.5) 

