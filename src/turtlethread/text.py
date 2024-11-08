import os 
import tempfile 
from opentypesvg import fonts2svg 

from .draw_svg import drawSVG 



# make it possible to at runtime process text 

class Fonts2SVGFakeOptions():
    def __init__(self, fontpath, outfolder):
        self.colors_list = ['#ffffff']
        self.output_folder_path = outfolder
        self.gnames_to_generate = []
        self.gnames_to_add = []
        self.gnames_to_exclude = []
        self.glyphsets_union = False
        self.adjust_view_box_to_glyph = False
        self.input_paths = [fontpath]
        self.font_paths_list = fonts2svg.validate_font_paths(self.input_paths)



class LetterDrawer(): 
    letter_gap = 0.2 

    def __init__(self, turtle): 
        self.turtle = turtle 

        self.loaded_fonts = {} 
        self.created_tmpdirs = [] 
        # equivalent to self.clear_fonts() 

        # TODO: default load some common fonts 

    # if we want to use .otf or whatever font files 
    def load_font(self, fontname='OpenDyslexic', fontpath='./turtlethread/fonts/OpenDyslexic_0_91_12_regular.otf'): 
        # LOAD A FONT GIVEN A FONTPATH, AND GIVE IT A NAME 
        td = tempfile.TemporaryDirectory() 
        self.created_tmpdirs.append(td) 
        tmpdirname = td.name 

        # processs text format: convert to svg first 

        opts = Fonts2SVGFakeOptions(fontpath=fontpath, outfolder=tmpdirname)
        font_paths_list = opts.font_paths_list
        hex_colors_list = opts.colors_list

        output_folder_path = fonts2svg.get_output_folder_path(opts.output_folder_path,
                                                        font_paths_list[0])

        fonts2svg.processFonts(font_paths_list, hex_colors_list, output_folder_path, opts) 
        # font SVGs are now in tmpdirname 


        # get the paths to the font SVGs 
        paths = {}
            
        for rt, _, files in os.walk(tmpdirname):
            for i in range(len(files)):
                try: 
                    paths[files[i][:files[i].index('.svg')]] = os.path.join(rt, files[i])
                except ValueError as ve: 
                    print("WARNING (GETTING SVGS):", ve) 

        self.loaded_fonts[fontname] = paths 

    def draw_one_letter(self, fontname, lettername, fontsize=20, colour='#000000', turtle=None): 
        if turtle is None: 
            if self.turtle is None: 
                raise ValueError("MUST DECLARE turtle TO USE IN LetterDrawer.draw_one_letter in either draw_one_letter() or LetterDrawer() init") 
            turtle = self.turtle 
        
        # DRAW ONE LETTER OF A FONT WITH A LOADED NAME, GIVEN A COLOUR 
        if fontname in self.loaded_fonts.keys(): 
            try: 
                drawSVG(turtle, self.loaded_fonts[fontname][lettername], fontsize, colour) 
                # TODO make it go back to start / next location? 
                # TODO maybe return the next location so that a letter sequence can be drawn 
            except Exception as e: 
                print("OR, it might be some other error({})".format(e))
                raise ValueError("font '{}' does not have the letter '{}'".format(fontname, lettername)) 
               
        else: 
            raise ValueError("font '{}' not loaded".format(fontname))
    
    def draw_letter_gap(self, fontsize): 
        with self.turtle.jump_stitch(): 
            currpos = list(self.turtle.position())
            self.turtle.goto(currpos[0] + LetterDrawer.letter_gap*fontsize, currpos[1])
        
    def draw_string(self, fontname, string, colour='#000000', turtle=None): 
        if turtle is None: 
            if self.turtle is None: 
                raise ValueError("MUST DECLARE turtle TO USE IN LetterDrawer.draw_one_letter in either draw_one_letter() or LetterDrawer() init") 
            turtle = self.turtle 

        # TODO: USE draw_one_letter TO DRAW 


    def clear_fonts(self): 
        for td in self.created_tmpdirs: 
            del td 
        self.created_tmpdirs = [] 
        self.loaded_fonts = {} 


