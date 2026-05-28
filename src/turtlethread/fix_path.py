from .turtle import Turtle 
from . import stitches 
import math 


class PathFixer: 
    
    @classmethod 
    def fix_path(cls, te:Turtle, min_turtle_dist:float=10, flip_y:bool=True): 
        new_te = Turtle() 
        fft = FixerFakeTurtle(PathFixer(new_te, min_turtle_dist, flip_y)) 
        te.fast_visualise(fft, annotate=False, setup_screen=False, skip=True, done=False, bye=False) 
        # setting turtle, annotate=False, setup_screen=False, done=False, bye=False make it not show the whole turtle dialog 
        # setting skip=True will let fast visualise have colour info 
        return new_te 
    
    def __init__(self, te:Turtle, min_turtle_dist:float=10, flip_y:bool=True): 
        
        self.te = te 
        
        self.flip_y = flip_y 
        self.min_turtle_dist = min_turtle_dist 

        self.debug = [] 
        self.save_to_debug = False 

        self.prev_turtle_pos = None 
        self.prev_end_pos = (0,0) #"PREV END POS"

        self.prev_stitch = None 


    def texcor(self): 
        return self.prev_end_pos[0] 
    def teycor(self): 
        if self.flip_y: 
            return -self.prev_end_pos[1]
        return self.prev_end_pos[1] 
    def teposition(self): 
        if self.flip_y: 
            return (self.prev_end_pos[0], -self.prev_end_pos[1])
        return self.prev_end_pos 


    def move_turtle_to(self, x, y): 

        #print("STITCH GROUP:", type(te._stitch_group_stack[-1])) 
        #print("(PREVIOUS: {})".format(str(self.prev_stitch_type))) 
        #print() 

        #print(self.prev_end_pos) 
        #print(self.prev_turtle_pos) 
        #print(te.position())
        #print(x, y)

        #debug.append((x, y)) # for self.debugging purposes 
        
        te = self.te 

        new_stitch = te._stitch_group_stack[-1] 

        diff_stitch_type = not ( (self.prev_stitch == None) or isinstance(new_stitch, type(self.prev_stitch)) ) 
        

        # first handle if we need to finish up the previous stitch as current is jump stitch 
        #print("DIFF STITCH TYPE:", diff_stitch_type)
        if diff_stitch_type: 
            #print("FROM {} TO {}".format(self.prev_stitch, type(new_stitch)))
            if isinstance(new_stitch, stitches.JumpStitch): 
                
                prevx, prevy = te.position() 
                if self.flip_y: 
                    prevy = -prevy # convert back to "normal" unflipped y 
                pex, pey = self.prev_end_pos 
                if abs(prevx - pex)<1e-7 and abs(prevy - pey)<1e-7: 
                    pass 
                else: 
                    #print("DRAWING {} FROM {} TO {}".format(self.prev_stitch, self.prev_turtle_pos, self.prev_end_pos)) 
                    #print("PREV STITCH:", self.prev_stitch)
                    #print(te._stitch_group_stack[-1])
                    with te.use_stitch_group(self.prev_stitch): 
                        # then finish this up first before the jump stitch 
                        pex, pey = self.prev_end_pos 
                        if self.save_to_debug: 
                            self.debug.append((pex, pey))
                        
                        if self.flip_y: 
                            te.goto(pex, -pey)
                        else: 
                            te.goto(pex, pey) 
                        
                        #print(te._stitch_group_stack[-1])
                        #print(te._stitch_group_stack[-1]._parent_stitch_group)
                        #print(self.prev_stitch)
                    
                    self.prev_turtle_pos = self.prev_end_pos
                self.prev_stitch = new_stitch 


        if isinstance(new_stitch, stitches.JumpStitch): 
            #print("JUMP STITCHING FROM {} TO {}".format(self.prev_turtle_pos, (x,y)))
            # if it's jump stitch then just go 
            if self.save_to_debug: 
                self.debug.append((None, None)) # this will signify a jump / switch hull
            if self.flip_y: 
                te.goto(x, -y) 
            else: 
                te.goto(x, y) 
            self.prev_turtle_pos = [x, y] 
            self.prev_stitch = new_stitch 
            self.prev_end_pos = x, y 
            return 

        # otherwise we need to see 
        currx, curry = self.prev_turtle_pos 
        xdiff = x-currx 
        ydiff = y-curry 
        mag = math.sqrt((xdiff)**2 + (ydiff)**2) # magnitude of difference vector 
        
        if ( mag >= self.min_turtle_dist): 

            pex, pey = self.prev_end_pos 
            if (abs(pex-currx) > 1e-7) or (abs(pey-curry) > 1e-7): # we should finish up the previous thing first 
                # different points, let's draw that first 
                if self.save_to_debug: 
                    self.debug.append((pex, pey))
                if self.flip_y: 
                    te.goto(pex, -pey) 

                else: 
                    te.goto(pex, pey) 
            

            # then travel the remaining distance -- split into steps so we can always use direct stitch 
            dx = x-pex 
            dy = y-pey 
            m = math.sqrt(dx*dx + dy*dy) 
            i = 1 
            while (i+1)*self.min_turtle_dist < m: 
                i += 1 
            fdx = dx/i 
            fdy = dy/i 
            for _ in range(i-1): 
                if self.save_to_debug: 
                    self.debug.append((pex+fdx*i, pey+fdy*i))
                if self.flip_y: 
                    te.goto(pex+fdx*i, -(pey+fdy*i))
                else: 
                    te.goto(pex+fdx*i, pey+fdy*i)
            if self.save_to_debug: 
                self.debug.append((x, y)) 
            if self.flip_y: 
                te.goto(x, -y) 
            else: 
                te.goto(x, y) 
            self.prev_turtle_pos = [x, y]
        
        self.prev_stitch = new_stitch 
        self.prev_end_pos = x, y 


class FixerFakeTurtle: 
    def __init__(self, pf:PathFixer): 
        self.pf = pf 
        self.jump = False 
        self.curr_color = None 
    
    def speed(self, *args, **kwargs): 
        pass 
    def _update(self, *args, **kwargs): 
        pass 
    def _tracer(self, *args, **kwargs): 
        pass 
    def setheading(self, *args, **kwargs): 
        pass
    def towards(self, *args, **kwargs): 
        return 1.0 
    def pensize(self, *args, **kwargs): 
        pass 
    def _delay(self, *args, **kwargs): 
        pass 
    
    def penup(self): 
        self.jump = True 
    def pendown(self): 
        self.jump = False 
    def color(self, c): 
        self.pf.te.color(c) 
        
    def position(self): 
        return self.pf.te.pos() 

    def goto(self, x, y): 
        if self.jump: 
            with self.pf.te.jump_stitch(): 
                self.pf.move_turtle_to(x, y) 
        else: 
            with self.pf.te.direct_stitch(): 
                self.pf.move_turtle_to(x, y) 

