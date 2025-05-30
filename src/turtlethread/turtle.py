import math
from contextlib import contextmanager
from enum import Enum
from warnings import warn

from pyembroidery import write, STITCH

from . import stitches
from . import fills
from .base_turtle import TNavigator, Vec2D
from .pattern_info import show_info
from .visualise import visualise_pattern, fast_visualise

USE_SPHINX_GALLERY = False


class ConfigValueMixin:
    NO_VALUE = object()

    @classmethod
    def get(cls, item, default=NO_VALUE):
        if isinstance(item, cls):
            return item
        valid_items = {enum.name.lower() for enum in cls}
        if item.lower() not in valid_items and default is cls.NO_VALUE:
            raise KeyError(f"{item} is not a valid {cls.__name__}. Must be one of {valid_items} (case insensitive)")
        elif item.lower() not in valid_items:
            return default

        return cls[item.upper()]


class AngleMode(ConfigValueMixin, Enum):
    RADIANS = "radians"
    DEGREES = "degrees"


class Turtle(TNavigator):
    """Turtle object that to make embroidery files. Mirrored after the official :py:mod:`turtle` library.

    This class has the same API as the builtin ``turtle.Turtle`` class with documented changes, for more information
    see the official documentation of the
    `builtin turtle library <https://docs.python.org/3/library/turtle.html#methods-of-rawturtle-turtle-and-corresponding-functions>`_

    One turtle-step is equivalent to 0.1 mm (unless scaled otherwise).

    Parameters
    ----------
    pattern : turtlethread.stitches.EmbroideryPattern (optional)
        The embroidery pattern to work with. If not supplied, then an empty pattern will be created.
    scale : float (optional, default=1)
        Scaling between turtle steps and units in the embroidery file. Below are some example scaling

         * `scale=1`  - One step is one unit in the embroidery file (0.1 mm)
         * `scale=10` - One step equals 1 mm
         * `scale=2`  - The scaling TurtleStitch uses
    angle_mode : "degrees" or "radians" (optional, default="degrees")
        How angles are computed.
    mode : "standard", "world" or "logo" (optional, default="standard")
        Mode "standard" is compatible with turtle.py.
        Mode "logo" is compatible with most Logo-Turtle-Graphics.
        Mode "world" is the same as 'standard' for TurtleThread.

        .. list-table::
            :header-rows: 1

            * - Mode
              - Initial turtle heading
              - Positive angles
            * - ``"standard"``
              - To the right (east)
              - Counterclockwise
            * - ``"logo"``
              - Upward (north)
              - Clockwise

    """

    def __init__(self, pattern=None, scale=1, angle_mode="degrees", mode=TNavigator.DEFAULT_MODE, color=None):
        # TODO: Flag that can enable/disable changing angle when angle mode is changed
        if pattern is None:
            self.pattern = stitches.EmbroideryPattern(scale=scale)
        else:
            self.pattern = pattern

        self.curr_color = color 

        # Set up stitch parameters prior to super.__init__ since self.reset() depends on stitch type
        self._stitch_group_stack = []

        super().__init__(mode=mode)
        self.angle_mode = angle_mode

        # For integration with sphinx-gallery
        self._gallery_patterns = []

        # Initialize fill variable
        self.filling = False
        self._fill_stitch_position_stack = []

    @property
    def angle_mode(self):
        """The angle mode, either "degrees" or "radians"."""
        if abs(self._degreesPerAU - 1) < 1e-5:
            return "degrees"
        elif abs(self._degreesPerAU - 360 / math.tau) < 1e-5:
            return "radians"
        else:
            return "other (_setDegreesPerAU has been called explicitly)"

    @angle_mode.setter
    def angle_mode(self, value):
        """Setter that ensures that a valid angle mode is used."""
        if not isinstance(value, (str, AngleMode)):
            raise TypeError(f"Angle mode must be one of 'degrees' or 'radians' (case insensitive), not {value}")

        if AngleMode.get(value, None) == AngleMode.DEGREES:
            self.degrees()
        elif AngleMode.get(value, None) == AngleMode.RADIANS:
            self.radians()
        else:
            raise KeyError(f"Angle mode must be one of 'degrees' or 'radians' (case insensitive), not {value}")

    @property
    def angle(self):
        return self.heading()

    @angle.setter
    def angle(self, value):
        self.setheading(value)

    def _steps_from_stitch_length(self, stitch_length, radius, extent):
        if radius == 0:
            steps = 1
        elif 0.5 * stitch_length / radius > math.sin(math.pi / 4):
            steps = 4
            warn(
                "Cannot calculate `steps` based on `stitch_length` as `stitch_length` is too long compared"
                + " to `radius`. A minimum no. `steps` of 4 is chosen instead. To disable this either provide"
                + " `steps`, decrease `stitch_length` or increase the circle `radius`"
            )
        else:
            extent = math.radians(extent * self._degreesPerAU)
            steps = self._n_sides_from_side_length(stitch_length, radius, extent)
            steps = int(round(steps))
        return steps

    def _n_sides_from_side_length(self, side_length, radius, extent):
        # Assumes that radius is converted to radians prior to call
        return extent / (2 * math.asin(0.5 * side_length / radius))

    def circle(self, radius, extent=None, steps=None):
        """Draw a circle or arc, for more info see the official :py:func:`turtle.circle` documentation.

        Parameters
        ----------
        radius: float
            Radius of the circle
        extent: float
            The angle of the arc, by default it is a full circle
        steps: float
            The circle is approximated as a sequence of ``steps`` line segments. If the ``steps`` are not given, then the optimal number
            of line segments for the current stitch length is selected.
        """
        if radius == 0:  # TODO: Maybe use a lower tolerance
            warn("Drawing a circle with radius is 0 is not possible and may lead to many stitches in the same spot")
        if math.isinf(radius) or math.isnan(radius):
            raise ValueError(f"``radius`` cannot be nan or inf, it is {radius}")

        if extent is None:
            extent = self._fullcircle

        if (
            steps is None
            and self._stitch_group_stack  # The stitch group stack is not empty
            and hasattr(self._stitch_group_stack[-1], "stitch_length")  # length is specified in topmost stitch group
        ):
            stitch_length = self._stitch_group_stack[-1].stitch_length
            steps = self._steps_from_stitch_length(stitch_length, abs(radius), extent)
        elif steps is None:
            steps = 20

        super().circle(radius=radius, extent=extent, steps=steps)

    def start_running_stitch(self, stitch_length=30):
        """Set the stitch mode to running stitch (not recommended, use ``running_stitch``-context instead).

        With a running stitch, we get stitches with a constant distance between each stitch.

        One step is equivalent to 0.1 mm, we recommend setting the minimum length
        between each stitch to 30 (3 mm).

        It is recommended to use the ``running_stitch``-context instead of the start-functions
        since they will automatically cleanup afterwards.

        Parameters
        ----------
        stitch_length : int
            Number of steps between each stitch.
        """
        self.set_stitch_type(stitches.RunningStitch(self.pos(), self.curr_color, stitch_length))

    def start_triple_stitch(self, stitch_length):
        """Set the stitch mode to triple stitch (not recommended, use ``triple_stitch``-context instead).

        Triple stitch is equivalent to running stitch, but the thread moves back and forth three times for each stitch.

        One step is equivalent to 0.1 mm, we recommend setting the minimum length between each stitch to 30 (3 mm).

        Parameters
        ----------
        stitch_length : int
            Number of steps between each stitch.
        """
        self.set_stitch_type(stitches.TripleStitch(self.pos(), self.curr_color, stitch_length))

    def start_jump_stitch(self):
        """Set the stitch mode to jump-stitch (not recommended, use ``jump_stitch``-context instead).

        With a jump-stitch, trim the thread and move the needle without sewing more stitches.
        """
        self.set_stitch_type(stitches.JumpStitch(self.pos())) # no need color for jump stitches 

    def start_zigzag_stitch(
        self,
        stitch_length: int | float,
        stitch_width: int | float,
        center: bool = False,
        auto_adjust: bool = True,
        enforce_end_stitch: bool = True,
        enforce_start_stitch: bool = True) -> None:
        """Set the stitch mode to zigzag stitch.""" 
        
        self.set_stitch_type(stitches.ZigzagStitch(
            self.pos(),
            self.curr_color, 
            stitch_length,
            stitch_width,
            center=center,
            auto_adjust=auto_adjust,
            enforce_end_stitch=enforce_end_stitch,
            enforce_start_stitch=enforce_start_stitch
        ))

    def start_satin_stitch(self, width, center = True):
        """Set the stitch mode to satin stitch.""" 
        self.set_stitch_type(stitches.SatinStitch(self.pos(), self.curr_color, width, center=center))

    def start_cross_stitch(
        self,
        stitch_length: int | float,
        stitch_width: int | float,
        center: bool = False,
        auto_adjust: bool = True,
        enforce_end_stitch: bool = True,
        enforce_start_stitch: bool = True) -> None:
        """Set the stitch mode to cross stitch.""" 
        
        self.set_stitch_type(stitches.CrossStitch(
            self.pos(),
            self.curr_color, 
            stitch_length,
            stitch_width,
            center=center,
            auto_adjust=auto_adjust,
            enforce_end_stitch=enforce_end_stitch,
            enforce_start_stitch=enforce_start_stitch
        ))

    def start_z_stitch(
        self,
        stitch_length: int | float,
        stitch_width: int | float,
        center: bool = False,
        auto_adjust: bool = True,
        enforce_end_stitch: bool = True,
        enforce_start_stitch: bool = True) -> None:
        """Set the stitch mode to z stitch.""" 
        
        self.set_stitch_type(stitches.ZStitch(
            self.pos(),
            self.curr_color, 
            stitch_length,
            stitch_width,
            center=center,
            auto_adjust=auto_adjust,
            enforce_end_stitch=enforce_end_stitch,
            enforce_start_stitch=enforce_start_stitch
        ))

    def start_direct_stitch(self):
        self.set_stitch_type(stitches.DirectStitch(self.pos()))
    
    def start_fast_direct_stitch(self):
        self.set_stitch_type(stitches.FastDirectStitch(self.pos()))

    def cleanup_stitch_type(self):
        """Cleanup after switching stitch type."""
        if self.filling: 
            for command in self._stitch_group_stack[-1].get_stitch_commands():
                if command[2] == 0: # pyembroidery.STITCH
                    self._fill_stitch_position_stack.append((command[0], command[1]))
                elif command[2] == 1: # after the jump
                    self._fill_stitch_position_stack.append((None, None)) # Indicates to reset

        self._stitch_group_stack.pop()
        if self._stitch_group_stack:
            # This handles nested context managers. We remove the top stitch group
            # from the stack and make a copy of it that we place back. We do it this
            # way so the starting position of the copy is where the the turtle is right
            # now.
            previous_stitch_group = self._stitch_group_stack.pop()
            stitch_group = previous_stitch_group.empty_copy(self.position())

            self._stitch_group_stack.append(stitch_group)
            self.pattern.stitch_groups.append(stitch_group)
            

    def set_stitch_type(self, stitch_group):
        self._stitch_group_stack.append(stitch_group)
        self.pattern.stitch_groups.append(stitch_group)

    @contextmanager
    def use_stitch_group(self, stitch_group):
        self.set_stitch_type(stitch_group=stitch_group)
        yield
        if (self._stitch_group_stack[-1]._parent_stitch_group is not stitch_group) and (self._stitch_group_stack[-1] is not stitch_group):
            raise RuntimeError(
                "Inconsistent state, likely caused by explicitly calling `cleanup_stitch_type` within a"
                + " stitch group context (e.g. within a `with turtle.running_stitch(20):` block)."
                + "\nYou should either set stitch groups with context managers or with the `start_{stitch_type}`"
                + " methods, not both."
            )

        self.cleanup_stitch_type()

    def running_stitch(self, stitch_length=30):
        """Set the stitch mode to running stitch and cleanup afterwards.

        With a running stitch, we get stitches with a constant distance between each stitch.

        One step is equivalent to 0.1 mm, we recommend setting the minimum length
        between each stitch to 30 (3 mm).

        Parameters
        ----------
        stitch_length : int
            Number of steps between each stitch.
        """
        return self.use_stitch_group(stitches.RunningStitch(self.pos(), self.curr_color, stitch_length))

    def triple_stitch(self, stitch_length):
        """Set the stitch mode to triple stitch and cleanup afterwards.

        Triple stitch is equivalent to running stitch, but the thread moves back and forth three times for each stitch.

        One step is equivalent to 0.1 mm, we recommend setting the minimum length between each stitch to 30 (3 mm).

        Parameters
        ----------
        stitch_length : int
            Number of steps between each stitch.
        """
        return self.use_stitch_group(stitches.TripleStitch(self.pos(), self.curr_color, stitch_length))

    def jump_stitch(self, skip_intermediate_jumps=True):
        """Set the stitch mode to jump-stitch and cleanup afterwards.

        With a jump-stitch, trim the thread and move the needle without sewing more stitches.

        Parameters
        ----------
        skip_intermediate_jumps : bool (optional, default=True)
            If True, then multiple jump commands will be collapsed into one jump command. This is useful in the cases
            where there may be multiple subsequent jumps with no stitches inbetween. Multiple subsequent jumps doesn't
            make sense but it can happen dependent on how you generate your patterns.
        """
        return self.use_stitch_group(stitches.JumpStitch(self.pos(), skip_intermediate_jumps=skip_intermediate_jumps))

    def zigzag_stitch(
        self,
        stitch_length: int | float,
        stitch_width: int | float,
        center: bool = False,
        auto_adjust: bool = True,
        enforce_end_stitch: bool = True,
        enforce_start_stitch: bool = True) -> None:
        """Set the stitch mode to zigzag stitch.""" 
        
        return self.use_stitch_group(stitches.ZigzagStitch(
            self.pos(),
            self.curr_color, 
            stitch_length,
            stitch_width,
            center=center,
            auto_adjust=auto_adjust,
            enforce_end_stitch=enforce_end_stitch,
            enforce_start_stitch=enforce_start_stitch
        ))

    def satin_stitch(self, width, center = True):
        """Set the stitch mode to satin stitch.""" 
        return self.use_stitch_group(stitches.SatinStitch(self.pos(), self.curr_color, width, center=center))

    
    def cross_stitch(
        self,
        stitch_length: int | float,
        stitch_width: int | float,
        center: bool = False,
        auto_adjust: bool = True,
        enforce_end_stitch: bool = True,
        enforce_start_stitch: bool = True) -> None:
        """Set the stitch mode to cross stitch.""" 
        
        return self.use_stitch_group(stitches.CrossStitch(
            self.pos(),
            self.curr_color, 
            stitch_length,
            stitch_width,
            center=center,
            auto_adjust=auto_adjust,
            enforce_end_stitch=enforce_end_stitch,
            enforce_start_stitch=enforce_start_stitch
        ))

    def z_stitch(
        self,
        stitch_length: int | float,
        stitch_width: int | float,
        center: bool = False,
        auto_adjust: bool = True,
        enforce_end_stitch: bool = True,
        enforce_start_stitch: bool = True) -> None:
        """Set the stitch mode to z stitch.""" 
        
        return self.use_stitch_group(stitches.ZStitch(
            self.pos(),
            self.curr_color, 
            stitch_length,
            stitch_width,
            center=center,
            auto_adjust=auto_adjust,
            enforce_end_stitch=enforce_end_stitch,
            enforce_start_stitch=enforce_start_stitch
        ))

    def direct_stitch(self):
        return self.use_stitch_group(stitches.DirectStitch(self.pos(), self.curr_color))
    
    def fast_direct_stitch(self):
        return self.use_stitch_group(stitches.FastDirectStitch(self.pos(), self.curr_color))

    @property
    def _position(self):
        return Vec2D(self.x, self.y)

    @_position.setter
    def _position(self, other):
        """Goto a given position, see the :py:meth:`goto` documentation for more info."""
        if self._stitch_group_stack:
            self._stitch_group_stack[-1].add_location(other)
        self.x, self.y = other

    def save(self, filename, color_inf_filename=None):
        """Save the embroidery pattern as an embroidery or image file.

        Saves the embroiery pattern to file. Supports standard embroidery file formats,
        such as ``.dst``, ``.jef`` and ``.pes``, and utility formats such as ``.png``,
        ``.svg`` and ``.txt``. For a full list of supported file formats, see the `pyembroidery documentation <https://github.com/EmbroidePy/pyembroidery#file-io>`_.

        Parameters
        ----------
        filename : str
        """
        if not USE_SPHINX_GALLERY:
            pyemb = self.pattern.to_pyembroidery() 
            write(pyemb, filename)
            if color_inf_filename: 
                write(pyemb, color_inf_filename)
        else:
            self._gallery_patterns.append((filename, self.pattern.to_pyembroidery()))
            if color_inf_filename: 
                raise Exception("Cannot write to .inf file if using SPHINX gallery!") 
        
        

    def home(self):
        """Move the needle home (position (0, 0)), for more info see the official :py:func:`turtle.home` documentation"""
        self.goto(0, 0)
        self.angle = 0

    def visualise(self, turtle=None, width=800, height=800, scale=1, speed=6, trace_jump=False, skip=False, check_density=True, done=True, bye=True):
        """Use the builtin ``turtle`` library to visualise this turtle's embroidery pattern.

        Parameters
        ----------
        pattern : pyembroidery.EmbPattern
            Embroidery pattern to visualise
        turtle : turtle.Turtle (optional)
            Python turtle object to use for drawing. If not specified, then the default turtle
            is used.
        width : int
            Canvas width
        height : int
            Canvas height
        scale : int
            Factor the embroidery length's are scaled by.
        speed : int
            Speed that the turtle object moves at.
        trace_jump : bool
            If True, then draw a grey line connecting the origin and destination of jumps.
        skip : bool
            If True, then skip the drawing animation and jump to the completed visualisation.
        check_density : bool
            If True, then check the density of the embroidery pattern. Recommended but slow.
        done : bool
            If True, then ``turtle.done()`` will be called after drawing.
        bye : bool
            If True, then ``turtle.bye()`` will be called after drawing.
        """
        try:
            visualise_pattern(
                self.pattern.to_pyembroidery(),
                turtle=turtle, width=width, height=height, scale=scale, speed=speed, trace_jump=trace_jump, skip=skip, 
                check_density=check_density, done=done, bye=bye
            )
        except Exception as e:
            print(e)
            # Errors when you close the window! Yikes
            pass
    
    def fast_visualise(self, turtle=None, width=800, height=800, scale=1, speed=6, extra_speed=1, trace_jump=False, skip=False, check_density=True, done=True, bye=True):
        """A fast version of the visualise() function, though it has undergone less testing.

        Parameters
        ----------
        pattern : pyembroidery.EmbPattern
            Embroidery pattern to visualise
        turtle : turtle.Turtle (optional)
            Python turtle object to use for drawing. If not specified, then the default turtle
            is used.
        width : int
            Canvas width
        height : int
            Canvas height
        scale : int
            Factor the embroidery length's are scaled by.
        speed : int
            Speed that the turtle object moves at.
        extra_speed : int 
            Extra speed boost on top of everything. Defaults to 1, which is no speed boost. 0 is infinite speed boost 
        trace_jump : bool
            If True, then draw a grey line connecting the origin and destination of jumps.
        skip : bool
            If True, then skip the drawing animation and jump to the completed visualisation.
        check_density : bool
            If True, then check the density of the embroidery pattern. Recommended but slow.
        done : bool
            If True, then ``turtle.done()`` will be called after drawing.
        bye : bool
            If True, then ``turtle.bye()`` will be called after drawing.
        """
        try:
            fast_visualise(
                self,
                turtle=turtle, width=width, height=height, scale=scale, speed=speed, extra_speed=extra_speed, trace_jump=trace_jump, skip=skip, 
                check_density=check_density, done=done, bye=bye
            )
        except Exception as e:
            print(e)
            # Errors when you close the window! Yikes
            pass

    def show_info(self):
        """Display information about this turtle's embroidery pattern."""
        show_info(self.pattern.to_pyembroidery(), scale=self.pattern.scale)

    def begin_fill(self, mode = fills.ScanlineFill(), closed=True):
        """After begin_fill is called, the turtle will track the stitches made until end_fill is called, afterwhich the polygon formed by the stitches will be filled.
        The current implementation of fill is limited to straight lines between points of the polygon. This works well for "straight" stitches like running stitch and
        satin stitch, but will not fill in the spaces formed in stitches such as zigzag stitch.
        
        Parameters
        ----------
        mode : turtlethread.fills.Fill (optional, default = fills.ScanlineFill())
            The fill mode to use. Refer to the API reference for the possible fills.
        closed : bool (optional, default=True)
            Whether or not to automatically close the shape in the event it is not closed.
            This must be set to False if jump stitches are used to create a fill with a hollowed part.
        """
        self.filling = True
        self.fill_mode = mode
        self.fill_closed = closed
        fill_start_pos = self.pos()
        self._fill_stitch_position_stack = [fill_start_pos]

    def end_fill(self):
        """End the current fill, and draw the filled polygon."""
        if self.filling:
            self.filling = False
            temp_fill_stack = self._fill_stitch_position_stack.copy()

            if len(self._stitch_group_stack) > 0:
                # Add everything from current stack
                for command in self._stitch_group_stack[-1].get_stitch_commands():
                    if command[2] == 0: # pyembroidery.STITCH
                        temp_fill_stack.append((command[0], command[1]))
                    elif command[2] == 1: # after the jump
                        temp_fill_stack.append((None, None)) # Indicates to reset

            # Close the polygon
            if self.fill_closed and abs(temp_fill_stack[0] - temp_fill_stack[-1]) > 1:
                temp_fill_stack.append(temp_fill_stack[0])
            
            self.fill_mode.fill(self, temp_fill_stack)


    def color(self, newcol: str): 
        if newcol == self.curr_color: 
            return  # make no change, to avoid asking the user to repeatedly change thread 
        # We need to change the stitch group so that the color change is reflected!
        if self._stitch_group_stack:
            previous_stitch_group = self._stitch_group_stack.pop()
            stitch_group = previous_stitch_group.empty_copy(self.position())
            stitch_group.color = newcol
            self._stitch_group_stack.append(stitch_group)
            self.pattern.stitch_groups.append(stitch_group)
        self.curr_color = newcol 



