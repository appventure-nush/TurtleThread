flip_y = True 
# in this file, everything is in python turtle coordinates, except when directly interfacing with te with .goto or .xcor/.ycor/.position() 


# this code uses code from this link: https://github.com/tfx2001/python-turtle-draw-svg/blob/master/main.py 
# attribution: 

# -*- coding: utf-8 -*-
# Author: tfx2001
# License: GNU GPLv3
# Time: 2018-08-09 18:27


debug = [] 


#import turtle 

import turtlethread 
from bs4 import BeautifulSoup


from PIL import Image

import fitz
from svglib import svglib
from reportlab.graphics import renderPDF

from concurrent.futures import ThreadPoolExecutor # to speed up computation 

import numpy as np 

import tempfile

import turtlethread.stitches 

WriteStep = 15  # 贝塞尔函数的取样次数
Xh = 0  # 记录前一个贝塞尔函数的手柄
Yh = 0
scale = (1, 1)
first = True
K = 32

import math 
prev_turtle_pos = None 
prev_end_pos = None #"PREV END POS"
min_turtle_dist = 10 

prev_stitch = None 


def move_turtle_to(te:turtlethread.Turtle, x, y): 
    global prev_stitch 
    global prev_turtle_pos 
    global prev_end_pos 
    #print("STITCH GROUP:", type(te._stitch_group_stack[-1])) 
    #print("(PREVIOUS: {})".format(str(prev_stitch_type))) 
    #print() 

    #print(prev_end_pos) 
    #print(prev_turtle_pos) 
    #print(te.position())
    #print(x, y)

    #debug.append((x, y)) # for debugging purposes 

    new_stitch = te._stitch_group_stack[-1] 

    diff_stitch_type = not ( (prev_stitch == None) or isinstance(new_stitch, type(prev_stitch)) ) 
    

    # first handle if we need to finish up the previous stitch as current is jump stitch 
    #print("DIFF STITCH TYPE:", diff_stitch_type)
    if diff_stitch_type: 
        #print("FROM {} TO {}".format(prev_stitch, type(new_stitch)))
        if isinstance(new_stitch, turtlethread.stitches.JumpStitch): 
            
            prevx, prevy = te.position() 
            if flip_y: 
                prevy = -prevy # convert back to "normal" unflipped y 
            pex, pey = prev_end_pos 
            if abs(prevx - pex)<1e-7 and abs(prevy - pey)<1e-7: 
                pass 
            else: 
                #print("DRAWING {} FROM {} TO {}".format(prev_stitch, prev_turtle_pos, prev_end_pos)) 
                with te.use_stitch_group(prev_stitch): 
                    # then finish this up first before the jump stitch 
                    pex, pey = prev_end_pos 
                    if flip_y: 
                        te.goto(pex, -pey)
                    else: 
                        te.goto(pex, pey) 
                
                prev_turtle_pos = prev_end_pos
            prev_stitch = new_stitch 


    if isinstance(new_stitch, turtlethread.stitches.JumpStitch): 
        #print("JUMP STITCHING FROM {} TO {}".format(prev_turtle_pos, (x,y)))
        # if it's jump stitch then just go 
        if flip_y: 
            te.goto(x, -y) 
        else: 
            te.goto(x, y) 
        prev_turtle_pos = [x, y] 
        prev_stitch = new_stitch 
        prev_end_pos = x, y 
        return 

    # otherwise we need to see 
    currx, curry = prev_turtle_pos 
    xdiff = x-currx 
    ydiff = y-curry 
    mag = math.sqrt((xdiff)**2 + (ydiff)**2) # magnitude of difference vector 
    
    if ( mag >= min_turtle_dist): 
        #print("DRAWING {} CONSIDERING MAG FROM {} TO {} MID STOP AT {}".format(new_stitch, prev_turtle_pos, (x,y), (currx + (min_turtle_dist/mag) * xdiff, (curry + (min_turtle_dist/mag) * ydiff) )))
        # travel that distance first 
        if flip_y: 
            te.goto(currx + (min_turtle_dist/mag) * xdiff, - (curry + (min_turtle_dist/mag) * ydiff) ) 

        else: 
            te.goto(currx + (min_turtle_dist/mag) * xdiff, (curry + (min_turtle_dist/mag) * ydiff) ) 

        # then travel the remaining distance 
        if flip_y: 
            te.goto(x, -y) 
        else: 
            te.goto(x, y) 
        prev_turtle_pos = [x, y]
    
    prev_stitch = new_stitch 
    prev_end_pos = x, y 

    


def Bezier(p1, p2, t):  # 一阶贝塞尔函数
    return p1 * (1 - t) + p2 * t


def Bezier_2(te, x1, y1, x2, y2, x3, y3):  # 二阶贝塞尔函数
    move_turtle_to(te, x1, y1)
    #te.pendown()
    for t in range(0, WriteStep + 1):
        x = Bezier(Bezier(x1, x2, t / WriteStep),
                   Bezier(x2, x3, t / WriteStep), t / WriteStep)
        y = Bezier(Bezier(y1, y2, t / WriteStep),
                   Bezier(y2, y3, t / WriteStep), t / WriteStep)
        move_turtle_to(te, x, y)

    ##te.penup()


def Bezier_3(te, startx, starty, x1, y1, x2, y2, x3, y3, x4, y4):  # 三阶贝塞尔函数
    x1 = startx + x1
    y1 = starty - y1
    x2 = startx + x2
    y2 = starty - y2
    x3 = startx + x3
    y3 = starty - y3
    x4 = startx + x4
    y4 = starty - y4  # 坐标变换
    move_turtle_to(te, x1, y1)
    #te.pendown()
    for t in range(0, WriteStep + 1):
        x = Bezier(Bezier(Bezier(x1, x2, t / WriteStep), Bezier(x2, x3, t / WriteStep), t / WriteStep),
                   Bezier(Bezier(x2, x3, t / WriteStep), Bezier(x3, x4, t / WriteStep), t / WriteStep), t / WriteStep)
        y = Bezier(Bezier(Bezier(y1, y2, t / WriteStep), Bezier(y2, y3, t / WriteStep), t / WriteStep),
                   Bezier(Bezier(y2, y3, t / WriteStep), Bezier(y3, y4, t / WriteStep), t / WriteStep), t / WriteStep)
        move_turtle_to(te, x, y)

    #te.penup()


def Moveto(te, startx, starty, x, y):  # 移动到svg坐标下（x，y）
    with te.jump_stitch(): 
        move_turtle_to(te, startx + x, starty - y)


def Moveto_r(te, dx, dy):
    #te.penup()
    with te.jump_stitch(): 
        if flip_y: 
            move_turtle_to(te, te.xcor() + dx, -te.ycor() - dy)
        else: 
            move_turtle_to(te, te.xcor() + dx, te.ycor() - dy)
    #te.pendown()


def line(te, startx, starty, x1, y1, x2, y2):  # 连接svg坐标下两点
    #te.penup()
    with te.jump_stitch(): 
        move_turtle_to(te, startx + x1, starty - y1)
    #te.pendown()
    with te.running_stitch(30): 
        move_turtle_to(te, startx + x2, starty - y2) 
    #te.penup()


def Lineto_r(te, dx, dy):  # 连接当前点和相对坐标（dx，dy）的点
    #te.pendown()
    with te.running_stitch(30): 
        if flip_y: 
            move_turtle_to(te, te.xcor() + dx, -te.ycor() - dy) 
        else: 
            move_turtle_to(te, te.xcor() + dx, te.ycor() - dy) 
    #te.penup()


def Lineto(te, startx, starty, x, y):  # 连接当前点和svg坐标下（x，y）
    #te.pendown()
    with te.running_stitch(30): 
        move_turtle_to(te, startx + x, starty - y) 
    #te.penup()


def Curveto(te, startx, starty, x1, y1, x2, y2, x, y):  # 三阶贝塞尔曲线到（x，y）
    #te.penup()
    X_now = te.xcor() - startx
    if flip_y: 
        Y_now = starty + te.ycor() 
    else: 
        Y_now = starty - te.ycor()
    Bezier_3(te, startx, starty, X_now, Y_now, x1, y1, x2, y2, x, y)
    global Xh
    global Yh
    Xh = x - x2
    Yh = y - y2


def Curveto_r(te, startx, starty, x1, y1, x2, y2, x, y):  # 三阶贝塞尔曲线到相对坐标（x，y）
    #te.penup()
    X_now = te.xcor() - startx 
    if flip_y: 
        Y_now = starty + te.ycor() 
    else: 
        Y_now = starty - te.ycor()
    Bezier_3(te, startx, starty, X_now, Y_now, X_now + x1, Y_now + y1,
             X_now + x2, Y_now + y2, X_now + x, Y_now + y)
    global Xh
    global Yh
    Xh = x - x2
    Yh = y - y2


def transform(w_attr):
    funcs = w_attr.split(' ')
    for func in funcs:
        func_name = func[0: func.find('(')]
        if func_name == 'scale':
            global scale
            scale = (float(func[func.find('(') + 1: -1].split(',')[0]),
                     -float(func[func.find('(') + 1: -1].split(',')[1]))


def readPathAttrD(w_attr):
    curr_parse = ''
    for i in w_attr:
        # print("now cmd:", i)
        if i == ' ':
            #print(float(curr_parse)) 
            yield float(curr_parse)
            curr_parse = ""
        elif i.isalpha():
            if (curr_parse):
                #print(float(curr_parse))
                yield float(curr_parse)
                curr_parse = ""
            #print(i) 
            yield i
        else:
            curr_parse += i



def drawSVG(te:turtlethread.Turtle, filename, height, w_color=None, thickness=1, fill=True, outline=False, fill_min_y_dist:int=10, fill_min_x_dist=10, full_fill=True, flip_y_in:bool=False): # TODO consider colour 
    # draws an SVG file with the turtle 
    #print("HI DRAWING SVG")

    global flip_y 
    flip_y = flip_y_in 
    #print("FLIP_Y:", flip_y)

    SVGFile = open(filename, 'r')
    SVG = BeautifulSoup(SVGFile.read(), 'lxml')
    viewbox = SVG.svg.attrs['viewbox'].split() # x y width height 
    Height = height #float(SVG.svg.attrs['height'][0: -2])
    Width = height * float(viewbox[2]) / float(viewbox[3]) #float(SVG.svg.attrs['width'][0: -2])
    if (SVG.svg.g and 'transform' in SVG.svg.g.attrs): 
        transform(SVG.svg.g.attrs['transform'])
    #if first:
        #te.setup(height=Height, width=Width)
        #te.setworldcoordinates(-Width / 2, 300, Width -
        #                       Width / 2, -Height + 300)
        #first = False
    #te.tracer(100)
    #te.pensize(1)
    #te.speed(10000)

    #turtle.speed(0) 
    #turtle.tracer(0,0)


    s = Height / float(viewbox[3]) 
    scale = [s, s]
    #print("SCALE:", scale) 

    startx, starty = float(viewbox[0])*scale[0], float(viewbox[1])*scale[1] 
    addsx, addsy = te.position() 

    global prev_turtle_pos 
    prev_turtle_pos = list(te.position()) 
    if flip_y: 
        prev_turtle_pos[1] = -prev_turtle_pos[1] 

    #print("INITIAL PREV TURTLE POS", prev_turtle_pos)

    startx += addsx 
    starty += addsy 

    if flip_y: 
        addsy = -addsy 

    scale[1] = -scale[1] 
    if flip_y: 
        
        starty = -starty 

    #print("START:", [startx, starty])


    #te.penup()

    # TODO: DEAL WITH FILL USING ZIGZAG/SATIN STITCH 


    #turtle.screensize(Width, Height)
    #screen = turtle.Screen() 


    global debug 
    # if it's fill 
    if fill: 
        if full_fill: 
            
            # deal with the hulls whatever 
            hulls = [] 
            for i in SVG.find_all('path'):
                attr = i.attrs['d'].replace('\n', ' ') 
                split_capital_z = attr.split('Z') 
                for idx in range(len(split_capital_z)-1): 
                    split_capital_z[idx] += 'Z' 
                split_both = []
                for aa in split_capital_z: 
                    add = aa.split('z') 
                    for idx in range(len(add)-1): 
                        add[idx] += 'z' 
                    split_both += add 

                #print(split_both)
                
                for eq_attr in split_both: 
                    if eq_attr == '': continue 
                    hulls += get_hulls(eq_attr, min_turtle_dist*1000/Height, filename, height, w_color, thickness, fill, outline, fill_min_y_dist, fill_min_x_dist, full_fill, flip_y_in) 
            
            #print("NUMBER OF HULLS:", len(hulls))

            '''print("GOT HULLS:")
            for h in hulls: 
                print(h) 
                print('\n')'''
            
            # figure out which is in which - treat as a forest i guess 
            parent = [i for i in range(len(hulls))] 
            root = [i for i in range(len(hulls))] 
            rank = [1 for _ in range(len(hulls))] 

            for i in range(len(hulls)-1): 
                for j in range(i+1, len(hulls)): 
                    # check if we already know their relationship 


                    res = which_is_inner_hull(hulls[i], hulls[j]) # this assumes the paths are convex hulls. I think it's close enough but TODO might have problems here 
                    if res == 1: 
                        # hulls[i] in hulls[j] 
                        if root[i] == root[j]: 
                            if rank[parent[i]] < rank[j]: 
                                # j is lower than parent[i], so the more immediate parent should be j. 
                                parent[i] = j 
                                rank[i] = rank[j] + 1 
                            # else it was a kind of unnecessary operation... 
                        else: 
                            root[i] = root[j] 
                            parent[i] = j 
                            rank[i] = rank[j] + 1 

                    elif res == 2: 
                        # hulls[j] in hulls[i]
                        if root[j] == root[i]:
                            if rank[parent[j]] < rank[i]:
                                # i is lower than parent[j], so the more immediate parent should be i.
                                parent[j] = i
                                rank[j] = rank[i] + 1
                            # else it was a kind of unnecessary operation... 
                        else:
                            root[j] = root[i]
                            parent[j] = i
                            rank[j] = rank[i] + 1 
                    
            # else, we just know that they are not ancestor/child. 
            # through this brute force we can figure out every ancestor/child combo 
            # and through this rank comparison we get every parent/child combo. 
            # so we've gotten our tree yay 
            # the top of each tree should be filled, except its children who are unfilled, except inside their children, their grandchildren are to be filled, and so on. 
            unique_roots = list(set(root)) 
            fill = [None for _ in range(len(hulls))] 
            def setfill(curr, val:bool): 
                nonlocal fill 
                fill[curr] = val 
                for pidx in range(len(parent)): 
                    if pidx==curr: continue 
                    if parent[pidx] == curr: 
                        # this is a child, should be the opposite 
                        setfill(pidx, not val)

            for ur in unique_roots: 
                setfill(ur, True) 
            
            if None in fill: 
                print("ERROR: None in fill:", fill) 
                raise ValueError("ERROR: NoneType in fill")

            # now combine the unfilled children with their filled parents 
            for fidx in range(len(fill)): 
                if not fill[fidx]: 
                    # find parent and combine with parent 
                    p = parent[fidx] 
                    # find shortest distance from start/end of child to parent 
                    child_pos = hulls[fidx][0] 
                    min_dist = -1 
                    best_idx = 0 
                    for pidx in range(len(hulls[p])): 
                        parent_pos = hulls[p][pidx]
                        dist = math.sqrt((child_pos[0]-parent_pos[0])**2 + (child_pos[1]-parent_pos[1])**2) 
                        if min_dist==-1 or dist<min_dist: 
                            min_dist = dist 
                            best_idx = pidx 

                    parent_dirn = hull_is_clockwise(hulls[p]) 
                    child_dirn = hull_is_clockwise(hulls[fidx]) 

                    if (parent_dirn ^ child_dirn):                     
                        # if opposite dirn, it works 
                        hulls[p] = hulls[p][:best_idx] + hulls[fidx] + hulls[p][best_idx:] # add child's path to parent's path 
                    else: 
                        # if same dirn, need to reverse dirn to make it work 
                        hulls[p] = hulls[p][:best_idx] + hulls[fidx][::-1] + hulls[p][best_idx:] # add child's path to parent's path 



            # now, fill all the paths that need to be filled 
            for fidx in range(len(fill)): 
                if fill[fidx]: 
                    #print("FILLING HULL", fidx) 
                    #print(hulls[fidx]) 
                    curr_pos = list(te.position())
                    moved_pts = [] 
                    for pt in hulls[fidx]: 
                        if flip_y: 
                            moved_pts.append((pt[0]+curr_pos[0], -pt[1]+curr_pos[1]))
                        else: 
                            moved_pts.append((pt[0]+curr_pos[0], pt[1]+curr_pos[1]))

                    #print(moved_pts) 
                    #print() 

                    te.ScanlineFill().fill(te, moved_pts) 

        else: 
            debug = [] 
            lines = svg_get_lines(filename, round(Width), round(Height), fill_min_x_dist, fill_min_y_dist) 
            #print("FILL LINES:", lines)

            with te.jump_stitch(): 
                move_turtle_to(te, startx+lines[0][0][0], starty+lines[0][0][1]) # get to right position 

            for p1, p2 in lines: 
                #with te.jump_stitch(): 
                #    #print("WITH JUMP STITCH:", te._stitch_group_stack[-1] )
                #    move_turtle_to(te, startx+p1[0], starty+p1[1]) 
                with te.running_stitch(99999): 
                    #print("WITH RUNNING STITCH:", te._stitch_group_stack[-1] )
                    move_turtle_to(te, startx+p2[0], starty+p2[1]) 
            
            '''
            # debug 
            xs = [d[0] for d in debug] 
            ys = [d[1] for d in debug] 
            print("FILL XYXY:", min(xs), min(ys), max(xs), max(ys)) 
            print("TARGET XYXY:", startx, starty, startx+round(Width), starty+round(Height))
            ''' 

    # re-initialize 
    global prev_end_pos 
    global prev_stitch 
    prev_end_pos = None #"PREV END POS"
    prev_stitch = None 


    # outline 
    # TODO: use satin stitch for thickness 
    starty += round(Height) # just to fix the calculations below, since the origin is somewhere else 
    if outline: 
        debug = [] 
        with te.running_stitch(30): # 99999 will make sure we won't have gaps 
            #te.color(w_color) # TODO SWITCH COLOUR OF TEXT 

            def get_position(): 
                posx, posy = te.position() 
                if flip_y: 
                    posy = -posy 
                return posx-startx, -posy+starty 

            firstpos = None 

            def set_firstpos(): 
                nonlocal firstpos
                firstpos = list(te.position())
                if flip_y: 
                    firstpos[1] = -firstpos[1] 
                firstpos[0] -= startx
                firstpos[1] *= -1
                firstpos[1] += starty 

            for i in SVG.find_all('path'):
                attr = i.attrs['d'].replace('\n', ' ')
                f = readPathAttrD(attr)
                lastI = ''
                for i in f:
                    #print(i) 
                    # if i.lower() in ['c', 'q', 'l', 'h' 'v', 'z']: 
                    #     set_firstpos() 
                    
                    if i == 'M':
                        #te.end_fill()
                        Moveto(te, startx, starty, next(f) * scale[0], next(f) * scale[1])
                        #te.begin_fill()
                        set_firstpos() 
                    elif i == 'm':
                        #te.end_fill()
                        Moveto_r(te, startx, starty, next(f) * scale[0], next(f) * scale[1])
                        set_firstpos() 
                        #te.begin_fill()
                    elif i == 'C':
                        Curveto(te, startx, starty, next(f) * scale[0], next(f) * scale[1],
                                next(f) * scale[0], next(f) * scale[1],
                                next(f) * scale[0], next(f) * scale[1])
                        lastI = i
                    elif i == 'c':
                        Curveto_r(te, startx, starty, next(f) * scale[0], next(f) * scale[1],
                                next(f) * scale[0], next(f) * scale[1],
                                next(f) * scale[0], next(f) * scale[1])
                        lastI = i
                    elif i == 'Q': 
                        X_now = te.xcor() #- startx
                        if flip_y: 
                            Y_now = -te.ycor() #starty - te.ycor()
                        else: 
                            Y_now = te.ycor() 
                        Bezier_2(te, X_now, Y_now, next(f) * scale[0] + startx, -next(f) * scale[1] + starty, 
                                next(f) * scale[0] + startx, -next(f) * scale[1] + starty) 
                    elif i == 'q': 
                        X_now = te.xcor() 
                        if flip_y: 
                            Y_now = -te.ycor() #starty - te.ycor()
                        else: 
                            Y_now = te.ycor() 
                        Bezier_2(te, X_now, Y_now, X_now + next(f) * scale[0], Y_now - next(f) * scale[1], 
                                X_now + next(f) * scale[0], Y_now - next(f) * scale[1],) 
                    elif i == 'L':
                        Lineto(te, startx, starty, next(f) * scale[0], next(f) * scale[1])
                    elif i == 'l':
                        Lineto_r(te, next(f) * scale[0], next(f) * scale[1])
                        lastI = i
                    elif i == 'H': 
                        if flip_y: 
                            Lineto(te, startx, starty, next(f) * scale[0], te.position()[1]+starty)
                        else: 
                            Lineto(te, startx, starty, next(f) * scale[0], -te.position()[1]+starty)
                    elif i == 'h':
                        Lineto_r(te, next(f) * scale[0], 0.0)
                        lastI = i
                    elif i == 'V': 
                        Lineto(te, startx, starty, te.position()[0]-startx, next(f) * scale[1])
                    elif i == 'v':
                        Lineto_r(te, 0.0, next(f) * scale[1])
                        lastI = i
                    elif i == 'Z' or i == 'z': 
                        Lineto(te, startx, starty, *firstpos)
                    elif lastI == 'C':
                        Curveto(te, startx, starty, i * scale[0], next(f) * scale[1],
                                next(f) * scale[0], next(f) * scale[1],
                                next(f) * scale[0], next(f) * scale[1])
                    elif lastI == 'c':
                        Curveto_r(te, startx, starty, i * scale[0], next(f) * scale[1],
                                next(f) * scale[0], next(f) * scale[1],
                                next(f) * scale[0], next(f) * scale[1])
                    elif lastI == 'L':
                        Lineto(te, startx, starty, i * scale[0], next(f) * scale[1])
                    elif lastI == 'l':
                        Lineto_r(te, i * scale[0], next(f) * scale[1])
                    else: 
                        print("ERROR", i)

        '''
        # debug 
        starty -= round(Height) # to fix calculations below 
        xs = [d[0] for d in debug] 
        ys = [d[1] for d in debug] 
        print("OUTLINE XYXY:", min(xs), min(ys), max(xs), max(ys)) 
        print("TARGET XYXY:", startx, starty, startx+round(Width), starty+round(Height))
        '''



    with te.jump_stitch(): 
        move_turtle_to(te, addsx+Width, addsy) 

    SVGFile.close()



    # save it somewhere, for testing 
    #te.visualise(done=False, bye=False)
    

    '''
    from pathlib import Path
    savepath = (Path(__file__).parent / "visualise_postscript" / "test_text.eps") 
    print("SAVING TO", savepath)
    screen.getcanvas().postscript(file=savepath)

    import time 
    time.sleep(100)

    for i in range(2):
        try:
            turtle.bye()
        except turtle.Terminator:
            pass'''

    #turtle.update() 
    
    #return screen 

    return 


# for debugging purposes only 
def _debug_drawSVG(te:turtlethread.Turtle, filename, height, w_color=None, thickness=1, fill=True, outline=False, fill_min_y_dist:int=10, fill_min_x_dist=10, full_fill=True, flip_y_in:bool=False, w_attr=None): 
    # draws an SVG file with the turtle 
    #print("HI DRAWING SVG")

    global flip_y 
    flip_y = flip_y_in 
    #print("FLIP_Y:", flip_y)

    SVGFile = open(filename, 'r')
    SVG = BeautifulSoup(SVGFile.read(), 'lxml')
    viewbox = SVG.svg.attrs['viewbox'].split() # x y width height 
    Height = height #float(SVG.svg.attrs['height'][0: -2])
    Width = height * float(viewbox[2]) / float(viewbox[3]) #float(SVG.svg.attrs['width'][0: -2])
    if (SVG.svg.g and 'transform' in SVG.svg.g.attrs): 
        transform(SVG.svg.g.attrs['transform'])
    


    s = Height / float(viewbox[3]) 
    scale = [s, s]
    #print("SCALE:", scale) 

    startx, starty = float(viewbox[0])*scale[0], float(viewbox[1])*scale[1] 
    addsx, addsy = te.position() 

    global prev_turtle_pos 
    prev_turtle_pos = list(te.position()) 
    if flip_y: 
        prev_turtle_pos[1] = -prev_turtle_pos[1] 

    #print("INITIAL PREV TURTLE POS", prev_turtle_pos)

    startx += addsx 
    starty += addsy 

    if flip_y: 
        addsy = -addsy 

    scale[1] = -scale[1] 
    if flip_y: 
        
        starty = -starty 


    # re-initialize 
    global prev_end_pos 
    global prev_stitch 
    prev_end_pos = None #"PREV END POS"
    prev_stitch = None 


    # outline 
    # TODO: use satin stitch for thickness 
    starty += round(Height) # just to fix the calculations below, since the origin is somewhere else 
    if outline: 
        debug = [] 
        with te.running_stitch(30): # 99999 will make sure we won't have gaps 
            #te.color(w_color) # TODO SWITCH COLOUR OF TEXT 

            def get_position(): 
                posx, posy = te.position() 
                if flip_y: 
                    posy = -posy 
                return posx-startx, -posy+starty 

            firstpos = None 

            def set_firstpos(): 
                nonlocal firstpos
                firstpos = list(te.position())
                if flip_y: 
                    firstpos[1] = -firstpos[1] 
                firstpos[0] -= startx
                firstpos[1] *= -1
                firstpos[1] += starty 

            f = readPathAttrD(w_attr)
            lastI = ''
            for i in f:
                #print(i) 
                # if i.lower() in ['c', 'q', 'l', 'h' 'v', 'z']: 
                #     set_firstpos() 
                
                if i == 'M':
                    #te.end_fill()
                    Moveto(te, startx, starty, next(f) * scale[0], next(f) * scale[1])
                    #te.begin_fill()
                    set_firstpos() 
                elif i == 'm':
                    #te.end_fill()
                    Moveto_r(te, startx, starty, next(f) * scale[0], next(f) * scale[1])
                    set_firstpos() 
                    #te.begin_fill()
                elif i == 'C':
                    Curveto(te, startx, starty, next(f) * scale[0], next(f) * scale[1],
                            next(f) * scale[0], next(f) * scale[1],
                            next(f) * scale[0], next(f) * scale[1])
                    lastI = i
                elif i == 'c':
                    Curveto_r(te, startx, starty, next(f) * scale[0], next(f) * scale[1],
                            next(f) * scale[0], next(f) * scale[1],
                            next(f) * scale[0], next(f) * scale[1])
                    lastI = i
                elif i == 'Q': 
                    X_now = te.xcor() #- startx
                    if flip_y: 
                        Y_now = -te.ycor() #starty - te.ycor()
                    else: 
                        Y_now = te.ycor() 
                    Bezier_2(te, X_now, Y_now, next(f) * scale[0] + startx, -next(f) * scale[1] + starty, 
                            next(f) * scale[0] + startx, -next(f) * scale[1] + starty) 
                elif i == 'q': 
                    X_now = te.xcor() 
                    if flip_y: 
                        Y_now = -te.ycor() #starty - te.ycor()
                    else: 
                        Y_now = te.ycor() 
                    Bezier_2(te, X_now, Y_now, X_now + next(f) * scale[0], Y_now - next(f) * scale[1], 
                            X_now + next(f) * scale[0], Y_now - next(f) * scale[1],) 
                elif i == 'L':
                    Lineto(te, startx, starty, next(f) * scale[0], next(f) * scale[1])
                elif i == 'l':
                    Lineto_r(te, next(f) * scale[0], next(f) * scale[1])
                    lastI = i
                elif i == 'H': 
                    if flip_y: 
                        Lineto(te, startx, starty, next(f) * scale[0], te.position()[1]+starty)
                    else: 
                        Lineto(te, startx, starty, next(f) * scale[0], -te.position()[1]+starty)
                elif i == 'h':
                    Lineto_r(te, next(f) * scale[0], 0.0)
                    lastI = i
                elif i == 'V': 
                    Lineto(te, startx, starty, te.position()[0]-startx, next(f) * scale[1])
                elif i == 'v':
                    Lineto_r(te, 0.0, next(f) * scale[1])
                    lastI = i
                elif i == 'Z' or i == 'z': 
                    Lineto(te, startx, starty, *firstpos)
                elif lastI == 'C':
                    Curveto(te, startx, starty, i * scale[0], next(f) * scale[1],
                            next(f) * scale[0], next(f) * scale[1],
                            next(f) * scale[0], next(f) * scale[1])
                elif lastI == 'c':
                    Curveto_r(te, startx, starty, i * scale[0], next(f) * scale[1],
                            next(f) * scale[0], next(f) * scale[1],
                            next(f) * scale[0], next(f) * scale[1])
                elif lastI == 'L':
                    Lineto(te, startx, starty, i * scale[0], next(f) * scale[1])
                elif lastI == 'l':
                    Lineto_r(te, i * scale[0], next(f) * scale[1])
                else: 
                    print("ERROR", i)


    with te.jump_stitch(): 
        move_turtle_to(te, addsx+Width, addsy) 

    SVGFile.close()



    return 





def svg_to_pil(svgname) -> Image.Image : 
    # Convert svg to pdf in memory with svglib+reportlab
    # directly rendering to png does not support transparency nor scaling
    drawing = svglib.svg2rlg(path=svgname)
    pdf = renderPDF.drawToString(drawing)

    # Open pdf with fitz (pyMuPdf) to convert to PNG
    doc = fitz.Document(stream=pdf)
    pix = doc.load_page(0).get_pixmap(alpha=True, dpi=300)

    with tempfile.NamedTemporaryFile(suffix='.png') as tmpf: 
        pix.save(tmpf.name)

        image = Image.open(tmpf.name) 
    #print("FINISHED SVG TO PIL")
    return image 

import fast_tsp 
def svg_get_lines(svgname, width:int, height:int, min_x_dist:int=10, min_y_dist:int=10): 

    image = svg_to_pil(svgname).resize((width, height)) 
    n = np.array(image) 

    all_xs = [] 

    # identify regions 
    r = 0 
    regions = [] 
    down = True # this is useless 
    while r < width: 
        all_xs.append(r) 
        if down: 
            prev = 0 
            prev1 = -1 
            for c in range(height): 
                if n[c,r,3] > 0: # not transparent 
                    if prev == 0: 
                        prev1 = c 
                    prev = 1 
                else: 
                    if prev == 1: # from non-transparent to transparent 
                        regions.append([(r,prev1), (r,c-1)]) 
                    prev = 0
            if prev==1: # end of edge 
                regions.append([(r,prev1), (r,c)]) 
            down = False 
        else: 
            prev = height-1 
            prev1 = height 
            for c in range(height-1, 0, -1): 
                if n[c,r,3] > 0: # not transparent 
                    if prev == 0: 
                        prev1 = c 
                    prev = 1 
                else: 
                    if prev == 1: # from non-transparent to transparent 
                        regions.append([(r,prev1), (r,c-1)]) 
                    prev = 0
            if prev==1: # end of edge 
                regions.append([(r,prev1), (r,c)]) 
            down = True 

        if (r >= width-1): # this was the last one 
            break 
        
        r = min(r+min_x_dist, width-1) # distance 5 apart (0.5mm) is the mdefault
        


    # now, split each region into points within it 
    pts = {} # x: [ys] 
    psum_c = {} # x: [prefix summed consecutives]
    for xy0, xy1 in regions: 
        x = xy0[0] 
        yrange = sorted([xy0[1], xy1[1]]) 
        n = yrange[1]-yrange[0] 
        num = max(1, int(n//min_y_dist) ) # num+1 will be number of points 
        d = 1 + (n%min_y_dist)/num
        if x not in pts.keys(): 
            pts[x] = [] 
        
        for i in range(num): 
            pts[x].append(yrange[0]+i*d) 
        pts[x].append(yrange[1]) 

        if x not in psum_c.keys(): 
            psum_c[x] = [num+1] 
        else: 
            psum_c[x].append(psum_c[x][-1] + num+1)
    
    xs = list(pts.keys()) 
    for x in xs: 
        pts[x].sort() 
    

    # then, make a graph of all those nodes and tsp it 
    # TODO potentially can also consider direction (horizontal/vertical) so double the amt of nodes 

    
    # now get adj matrix 
    INF = 1000000 
    adjmat = [] 
    nums = {} # (x,y) -> num 
    poss = {} # num -> (x,y)
    next_num = 0 

    for xidx in range(len(xs)): 
        x = xs[xidx]
        cons_starts = psum_c[x] # doesn't include 0 but it'll throw error and except if 0 so it's fine 
        cons_ends = [i-1 for i in cons_starts] 

        allx_xidx = all_xs.index(x) 
        for yidx in range(len(pts[x])): 
            y = pts[x][yidx] 

            #print((x,y), "NOT TRANSPARENT")
            nums[(x, y)] = next_num 
            poss[next_num] = (x,y) 
            next_num += 1 

            # get idxs of adjacent ones 
            adjidxs = []
            # try the 4 diff moves 
            for dxp in range(-1,2): 
                for dyp in range(-1, 2): 
                    if (dyp==-1) and (yidx in cons_starts): continue 
                    if (dyp==1) and (yidx in cons_ends): continue 
                    new_allx_xidx = allx_xidx+dxp 

                    if all_xs[new_allx_xidx] not in xs: continue # not side by side xs 
                    try: 
                        new_x = all_xs[new_allx_xidx]
                        # try to find a y that's close enough 
                        if dyp==-1: 
                            for new_y in pts[new_x]: 
                                if abs(y-new_y) < 2*min_y_dist: 
                                    # consider it valid 
                                    q = (new_x, new_y)
                                    adjidxs.append(nums[q]) 
                    except: 
                        pass # it means doesnt exist 

            # add to adjmat 
            #print("ADJMAT")
            #print(adjmat) 
            #print("NEXT NUM:", next_num)
            for i in range(next_num-1): 
                if i in adjidxs: 
                    # adjacent; dist is 1 
                    adjmat[i].append(1) 
                else: 
                    adjmat[i].append(INF) 
            
            newrow = [INF for _ in range(next_num)] 
            for adjidx in adjidxs: 
                newrow[adjidx] = 1 
            newrow[-1] = 0 # self 
            adjmat.append(newrow)
    
    #print("ADJMAT") 
    #print(np.array(adjmat))
    # adjmat gotten, now solve 
    try: 
        tour = fast_tsp.find_tour(adjmat) 
    except Exception as e: 
        print("\n\n\nERROR GENERATING FILL PATH:\n")
        raise e 
        
    # convert tour to path with poss 
    lines = [] 
    prev_pos = poss[tour[0]] 
    for i in range(len(tour)-1): 
        lines.append((prev_pos, poss[tour[i]])) 
        prev_pos = poss[tour[i]] 
    return lines 



# stuff with convex hulls 
def get_hulls(w_attr, min_dist, filename, height, w_color=None, thickness=1, fill=True, outline=False, fill_min_y_dist:int=10, fill_min_x_dist=10, full_fill=True, flip_y_in:bool=False): 
    hulls = [] 

    # re-initialize 
    global prev_turtle_pos 
    global prev_end_pos 
    global prev_stitch 
    prev_turtle_pos = None 
    prev_end_pos = None #"PREV END POS"
    prev_stitch = None 

    global flip_y 
    real_flip_y = flip_y 
    flip_y = False 

    # run the whole outlining code with turtle identically, except we don't actually do it 
    ttt = turtlethread.Turtle() 
    _debug_drawSVG(ttt, filename, height, w_color, thickness, False, True, fill_min_y_dist, fill_min_x_dist, full_fill, flip_y_in, w_attr=w_attr)
    hull = [] 
    for x, y, _ in ttt.pattern.to_pyembroidery().stitches: 
        hull.append((x,y))
    
    if len(hull)>1: 
        hulls.append(hull) 

    # reset to normal 
    flip_y = real_flip_y 

    return hulls # can be empty, which means no hull 


'''

    hulls = [] 
    curr_hull = [] 
    vals = [] 

    print(w_attr)

    prev_xy = []#start_xy 

    #f = readPathAttrD(w_attr)
    #lastI = ''
    #for i in f:
    #    vals.append((next(f), next(f)))

    curr_letter = "" 
    curr_parse = ''
    for i in w_attr:
        if i == ' ':
            vals.append(float(curr_parse)) 
            curr_parse = ""
        elif i.isalpha():
            if (curr_parse):
                vals.append(float(curr_parse)) 
                curr_parse = ""
            
            # now process the previous letter 
            if len(vals) > 0 and curr_letter != "": 

                try: 
                    prev_xy = curr_hull[-1] 
                except: 
                    pass 

                if curr_letter.upper() == curr_letter: 
                    # uppercase --> absolute positions 
                    
                    if curr_letter == 'H': 
                        curr_hull.append([vals[0], prev_xy[1]]) 
                    elif curr_letter == 'V': 
                        curr_hull.append([prev_xy[0], vals[0]]) 
                    elif curr_letter in ['M', 'Z']: 
                        pass 
                    else: # should contain xs and ys 
                        for ii in range(len(vals)//2): 
                            curr_hull.append([vals[2*ii], vals[1+2*ii]]) 
                
                else: 
                    # lowercase --> relative positions 
                    if curr_letter == 'h': 
                        curr_hull.append([vals[0]+prev_xy[0], prev_xy[1]]) 
                    elif curr_letter == 'v': 
                        curr_hull.append([prev_xy[0], prev_xy[1] + vals[0]]) 
                    elif curr_letter in ['m', 'z']: 
                        pass 
                    else: # should contain xss and ys 
                        for ii in range(len(vals)//2): 
                            curr_hull.append([prev_xy[0]+vals[2*ii], prev_xy[1]+vals(1+2*ii)])

            curr_letter = i 

            if curr_letter.lower() == 'z': 
                # hull complete! 
                hulls.append(clean_hull(curr_hull, min_dist)) 
                curr_hull = [] 

        else:
            curr_parse += i
        

        # now process the previous letter 
        if len(vals) > 0 and curr_letter != "": 

            try: 
                prev_xy = curr_hull[-1] 
            except: 
                pass 
            
            if curr_letter.upper() == curr_letter: 
                # uppercase --> absolute positions 
                
                if curr_letter == 'H': 
                    curr_hull.append([vals[0], prev_xy[1]]) 
                elif curr_letter == 'V': 
                    curr_hull.append([prev_xy[0], vals[0]]) 
                elif curr_letter in ['M', 'Z']: 
                    pass 
                else: # should contain xs and ys 
                    for i in range(len(vals)//2): 
                        curr_hull.append([vals[2*i], vals[1+2*i]]) 
            
            else: 
                # lowercase --> relative positions 
                if curr_letter == 'h': 
                    curr_hull.append([vals[0]+prev_xy[0], prev_xy[1]]) 
                elif curr_letter == 'v': 
                    curr_hull.append([prev_xy[0], prev_xy[1] + vals[0]]) 
                elif curr_letter in ['m', 'z']: 
                    pass 
                else: # should contain xss and ys 
                    for i in range(len(vals)//2): 
                        curr_hull.append([prev_xy[0]+vals[2*i], prev_xy[1]+vals(1+2*i)])

    # hull complete! 
    if len(curr_hull) > 1: # it has to be >1 else of course it isn't valid 

        hulls.append(clean_hull(curr_hull, min_dist)) 

    return hulls # list of [x,y] coordinates 

def clean_hull(curr_hull, min_dist): 
    # clean up curr_hull 
    cleaned_hull = [] 
    cleaned_hull.append(curr_hull[0]) 
    prev_pos = curr_hull[0]
    for pidx in range(1, len(curr_hull)): 
        x, y = curr_hull[pidx] 
        currx, curry = prev_pos 
        xdiff = x-currx 
        ydiff = y-curry 
        mag = math.sqrt((xdiff)**2 + (ydiff)**2) # magnitude of difference vector 
    
        if ( mag >= min_dist ): 
            cleaned_hull.append([x,y]) 
            prev_pos = [x,y]

    print("CLEANED HULL LENGTH:", len(cleaned_hull))
    return cleaned_hull
'''


small_num = 1e-9
def which_is_inner_hull(h1, h2, recursed=False): 
    #print("WHICH IS INNER HULL")
    # pick 2 points from h2 to form a line 
    pt1, pt2 = h2[:2] 

    # get the x range 
    h2xs = sorted([pt1[0], pt2[0]]) 

    # y = mx + c 
    m_2 = (pt2[1]-pt1[1])/(pt2[0]-pt1[0] + small_num) # dy / dx 
    c_2 = pt1[1] - m_2*pt1[0] # c = y - mx 

    left_sat = False 
    right_sat = False 
    
    # now check every line segment in h1 and see if it intersects 
    for i1 in range(len(h1)): 
        i2 = (i1+1)%(len(h1)) 
        # the line segment is i1 to i2 
        m = (h1[i2][1]-h1[i1][1])/(h1[i2][0]-h1[i1][0] + small_num) # dy/dx 
        c = h1[i1][1] - m*h1[i1][0] # c = y - mx 

        # m x + c = m_2 x + c_2 => (m-m_2)x = c_2 - c => x = (c_2-c)/(m-m_2) 
        reqx = (c_2-c)/(m-m_2 + small_num) 

        # check if it's within max and min 
        minx, maxx = sorted([h1[i1][0], h1[i2][0]]) 
        if ((minx <= reqx) and (reqx <= maxx)): 
            # FULFILLED --> INTERSECTED WITHIN --> LET'S SEE IF MORE OUTSIDE THAN THE PTS 
            if ((h2xs[0] <= reqx) and (reqx <= h2xs[1])): 
                # INTERSECTED WITHIN IT 
                # SO H1 IS WITHIN H2 
                return 1 

            # it's intersecting not within, in at one of the directions (so actl it might just be disjoint still)
            if (reqx < h2xs[0]): 
                left_sat = True 
            else: 
                right_sat = True 
            
            if (left_sat and right_sat): 
                return 2 # it's intersecting not within on both sides, so it must be h2 inside h1 
    
    # still inconclusive --> there's no way 2 is within 1 i guess 
    if not recursed: # not using recursion to check again 
        # let's check if 1 is within 2 
        if which_is_inner_hull(h2, h1, recursed=True) == 2: # this means h1 is the inner one 
            return 1 
    
    # if it's here because it's recursive, we don't need to care about possibility of 1 since we only care abt 2 
    
    return 0 # they're disjoint (if recursive, it can't be 2. if not recursive, it can neither be 1 nor 2.) 



def hull_is_clockwise(hull): # credits to https://stackoverflow.com/questions/1165647/how-to-determine-if-a-list-of-polygon-points-are-in-clockwise-order 
    s = 0 
    for i in range(len(hull)): 
        x1, y1 = hull[i] 
        x2, y2 = hull[(i+1)%len(hull)] 
        s += (x2-x1)*(y2+y1) 
    
    return s>0 # True is mostly clockwise, False is mostly anticlockwise 



