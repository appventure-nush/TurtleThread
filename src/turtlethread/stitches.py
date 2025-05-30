from __future__ import annotations

import itertools
import math
from abc import ABC, abstractmethod
from copy import copy
from typing import Any, Generator, Iterable

try:
    from typing import Literal, Self, TypeAlias
except ImportError:
    from typing_extensions import Literal, Self, TypeAlias

import pyembroidery

from .base_turtle import Vec2D

# STITCH=0, JUMP=1, TRIM=2, ZIGZAG=3, SATIN=4, CROSS=5, Z=6
StitchCommand: TypeAlias = Literal[0, 1, 2, 3, 4, 5, 6]


class EmbroideryPattern:
    """Abstract representation of an embroidery pattern.

    Container object

    Parameters
    ----------
    scale: int (optional, default=1)
        All coordinates are multiplied by this parameter before converting it to a PyEmbroidery pattern.
        This is useful to control the number of steps per mm (default is 10 steps per mm).
    """

    def __init__(self, scale: int = 1) -> None:
        self.stitch_groups: list[StitchGroup | EmbroideryPattern] = []
        self.scale = scale

    def to_pyembroidery(self) -> pyembroidery.EmbPattern:
        """Convert to a PyEmbroidery pattern."""
        pattern = pyembroidery.EmbPattern()
        for stitch_group in self.stitch_groups:
            if (not isinstance(stitch_group, JumpStitch)) and stitch_group.color is not None: 
                change_col = True 
                if len(pattern.threadlist) > 0: 
                    change_col = (pattern.threadlist[-1].hex_color() != pyembroidery.EmbThread(stitch_group.color).hex_color())
                
                if change_col: 
                    pattern += stitch_group.color 

            scaled_stitch_commands = (
                (x * self.scale, y * self.scale, cmd) for x, y, cmd in stitch_group.get_stitch_commands()
            )
            pattern.stitches.extend(scaled_stitch_commands)

        return pattern

    def get_pyembroidery_of(self, stitch_group_idx): 
        """Get the PyEmbroidery pattern with the stitch commands of the i-th stitch group"""
        pattern = pyembroidery.EmbPattern()
        stitch_group = self.stitch_groups[stitch_group_idx]
        if (not isinstance(stitch_group, JumpStitch)) and stitch_group.color is not None: 
            pattern += stitch_group.color 

        scaled_stitch_commands = (
            (x * self.scale, y * self.scale, cmd) for x, y, cmd in stitch_group.get_stitch_commands()
        )
        pattern.stitches.extend(scaled_stitch_commands)

        return pattern

    def get_stitch_command(self) -> list[tuple[float, float, StitchCommand]]:
        """Get stitch commands for PyEmbroidery.

        This function is used when embroidery patterns contain whole embroidery patterns. If you're not explicitly
        making patterns within patterns, then you probably want to use the :py:meth:`to_pyembroidery` method instead.
        """
        for stitch_group in self.stitch_groups:
            yield from stitch_group.get_stitch_commands()


class StitchGroup(ABC):
    speedup=0 
    """Object representing one contiguous set of commands for the embroidery machine.

    Stitch groups are used to convert the Turtle commands into embroidery machine commands. For example, if you want to
    embroider with a running stitch, then you'd create a stitch group for a running stitch with the corresponding
    stitch length.

    Stitch groups work by storing subsequent locations of the Turtle and converts them into embroidery commands.

    Parameters
    ----------
    start_pos: Vec2D (tuple[float, float])
        The initial position of the turtle.
    """

    def __init__(self, start_pos: Vec2D, color: str) -> None:
        self._start_pos = start_pos
        self._positions = []
        self._stitch_commands = None
        self._parent_stitch_group = self
        self.color = color 

    def add_location(self, location: Vec2D) -> None:
        """Add a new location to this stitch group."""
        self._stitch_commands = None
        self._positions.append(location)

    @abstractmethod
    def _get_stitch_commands(self) -> list[tuple[float, float, StitchCommand]]:
        raise NotImplementedError

    def get_stitch_commands(self) -> list[tuple[float, float, StitchCommand]]:
        """Get the list of PyEmbroidery stitch commands for this stitch group"""
        if self._stitch_commands is None:
            self._stitch_commands = self._get_stitch_commands()

        return self._stitch_commands.copy()

    def empty_copy(self, start_pos) -> Self:
        """Create a copy of the stitch group but with no stored locations (i.e. no stitches)."""
        copied_group = copy(self)
        copied_group._positions = []
        copied_group._start_pos = start_pos
        copied_group._stitch_commands = None
        copied_group._parent_stitch_group = self._parent_stitch_group
        copied_group.color = self.color

        return copied_group


class UnitStitch(StitchGroup):
    """Class to represent stitches that are built off repeating a single pattern, e.g. zigzag, cross stitches.

    Given the distance to travel, the stitch will be repeated the required number of times to reach that distance.

    Contains a starting stitch and an ending stitch function. These functions will be called once at the start and
    end of the overall stitch, respectively. This is useful, for example, for centering stitches.

    Parameters
    ----------
    stitch_length : int
        Number of steps between each unit stitch, in the direction of travel. If auto-adjustment is not enabled, this
        will be the exact number of steps between each unit stitch.
    auto_adjust : bool (optional, default=True)
        If True, the stitch length will be automatically adjusted to a multiple of the distance travelled. Useful
        when only drawing a single forward or backwards stitch. 
        If False, the stitch length will be exactly ``stitch_length``. A final stitch will be added to the end position
        unless enforce_end_position is False.
    enforce_end_stitch : bool (optional, default=True)
        If True, the final stitch must be positioned at the end position. This will ensure that the total length of the
        stitch is the total distance to be traveled. 
        If False, there is no such guarantee. Any ending stitch will not occur.
        Useful in conjunction with enforce_start_stitch, to seamlessly blend two stitches together.
    enforce_start_stitch : bool (optional, default=True)
        If True, the first stitch must be positioned at the start position. 
        If False, the starting stitch pattern will not occur.

    Internal Attributes
    -------------------
    stitch_stop_multiplier : float (default=0)
        When stitching, the unit stitch will be repeated until there is stitch_stop_multiplier * stitch_length left to
        stitch. Useful when implementing an ending stitch pattern.
    x : int | float
        The current x position of the turtle. Used for _start_stitch_unit and _end_stitch_unit.
    y : int | float
        The current y position of the turtle. Used for _start_stitch_unit and _end_stitch_unit.
    distance_traveled : int | float
        The distance travelled by the turtle. Used for _start_stitch_unit and _end_stitch_unit.
    """
    def __init__(
        self, 
        start_pos: Vec2D, 
        color:str, 
        stitch_length: int | float, 
        auto_adjust: bool = True, 
        enforce_end_stitch: bool = True, 
        enforce_start_stitch: bool = True, ) -> None:

        super().__init__(start_pos=start_pos, color=color)
        self.stitch_length = stitch_length
        self.auto_adjust = auto_adjust
        self.enforce_end_stitch = enforce_end_stitch
        self.enforce_start_stitch = enforce_start_stitch

        self.stitch_stop_multiplier = 0
        self.x = start_pos[0]
        self.y = start_pos[1]
        self.distance_traveled = 0

    @classmethod
    def round_stitch_length(cls, stitch_length : int | float, distance : int | float):
        """Method to round the stitch length to a multiple of the distance.

        Parameters
        ----------
        stitch_length : int | float
            The stitch length to round.
        distance : int | float
            The distance of travel.
        """
        if distance < stitch_length: 
            # Stitch length cannot be less than the total distance
            return distance 

        # Find the closest stitch_length that is a multiple of stitch_length
        return distance / round(distance/stitch_length)
         
    def _start_stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float) -> list[tuple[float, float, StitchCommand]]:
        """Stitch a pattern at the start of a stitch. To be implemented by children.
        The stitch should start from start_pos, but should not have a stitch at that position.
        There should be a stitch at the end position.

        Due to the many variations in the distance travelled in this section, children should directly modify 
        self.x and self.y, which should be set to the end position after the starting stitch pattern, as well as
        self.distance_traveled to set the distance travelled along the direction of the stitch.

        Parameters
        ----------
        start_pos: Vec2D (tuple[float, float])
            The start position of the stitch.
        angle: float    
            The angle of the stitch.
        stitch_length: float
            The stitch length of the stitch.
        """
        return iter(())
        
    def _stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float) -> list[tuple[float, float, StitchCommand]]:
        """Stitch a single unit. To be implemented by children.
        The stitch should start from start_pos, but should not have a stitch at that position.
        There should be a stitch at the end position.

        Parameters
        ----------
        start_pos: Vec2D (tuple[float, float])
            The start position of the stitch.
        angle: float    
            The angle of the stitch.
        stitch_length: float
            The stitch length of the stitch.
        """
        raise NotImplementedError

    def _end_stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float, distance: float) -> list[tuple[float, float, StitchCommand]]:
        """Stitch a pattern at the start of a stitch. To be implemented by children.
        The stitch should start from start_pos, but should not have a stitch at that position.
        There should NOT be a stitch at the end position.

        Due to the many variations in the distance travelled in this section, children should directly modify 
        self.x and self.y, which should be set to the end position after the starting stitch pattern, as well as
        self.distance_traveled to set the distance travelled along the direction of the stitch.

        Parameters
        ----------
        start_pos: Vec2D (tuple[float, float])
            The start position of the stitch.
        angle: float    
            The angle of the stitch.
        stitch_length: float
            The stitch length of the stitch.
        distance: float
            The distance to the end position.
        """
        return iter(()) # Return an empty iterator as a sane default
    
    def _iter_stitches_between_positions(
        self, position_1: Vec2D, position_2: Vec2D
    ) -> Generator[tuple[StitchCommand, float, float], None, None]:

        x, y = position_1
        x_end, y_end = position_2

        distance = math.sqrt((x - x_end) ** 2 + (y - y_end) ** 2)
        angle = math.atan2(y_end - y, x_end - x)
        dx = math.cos(angle)
        dy = math.sin(angle)

        distance_traveled = 0
        stitch_length = self.stitch_length
        if self.auto_adjust: # Adjust stitch length if auto-adjustment is enabled
            stitch_length = self.round_stitch_length(self.stitch_length, distance)

        # Perform start stitches
        self.x = x
        self.y = y
        self.distance_traveled = distance_traveled

        start_stitches = self._start_stitch_unit(Vec2D(x, y), angle, stitch_length)
        if start_stitches is not None:
            for stitch in start_stitches: yield stitch

        x = self.x
        y = self.y
        distance_traveled = self.distance_traveled

        # Repeat until stitch_stop_multiplier*stitch_length away
        # NOTE: If stitch_stop_multiplier is 0, the stitch length will be a multiple of the distance so we can stop on the end point itself
        while (self.stitch_stop_multiplier == 0 and distance_traveled + stitch_length*self.stitch_stop_multiplier < distance) or (self.stitch_stop_multiplier > 0 and distance_traveled + stitch_length*self.stitch_stop_multiplier <= distance):
            for stitch in self._stitch_unit(Vec2D(x, y), angle, stitch_length): yield stitch
            x += stitch_length * dx
            y += stitch_length * dy
            distance_traveled += stitch_length

        # Do not do end stitches if the unit stitch reaches the final destination
        if (distance_traveled < distance or (math.isclose(distance_traveled, distance, rel_tol=0.001))) and self.enforce_end_stitch:
            self.x = x
            self.y = y
            self.distance_traveled = distance_traveled

            end_stitches = self._end_stitch_unit(Vec2D(x, y), angle, stitch_length, distance-distance_traveled)
            if end_stitches is not None:
                for stitch in end_stitches: yield stitch
            yield x_end, y_end, pyembroidery.STITCH


    def _get_stitch_commands(self) -> list[tuple[float, float, StitchCommand]]:
        if not self._positions:
            return []

        stitch_commands = []

        # Start the stitch at the start position if enforce_start_stitch is True.
        if self.enforce_start_stitch:
            stitch_commands.append((self._start_pos[0], self._start_pos[1], pyembroidery.STITCH))

        stitch_commands.extend(self._iter_stitches_between_positions(self._start_pos, self._positions[0]))
        for pos1, pos2 in itertools.pairwise(self._positions):
            stitch_commands.extend(self._iter_stitches_between_positions(pos1, pos2))

        return stitch_commands


class RunningStitch(StitchGroup):
    """Stitch group for running stitches.

    With a running stitch, we get stitches with a constant distance between each stitch.

    If the turtle is supposed to move a number of steps that is not a multiple of ``stitch_length``, then all but the
    last stitch in that stretch will have the same length and the last stitch will be between ``0.5*stitch_length`` and
    ``1.5*stitch_length``.

    Parameters
    ----------
    stitch_length : int
        Number of steps between each stitch.
    """

    def __init__(self, start_pos: Vec2D, color:str, stitch_length: int | float) -> None:
        super().__init__(start_pos=start_pos, color=color)

        self.stitch_length = stitch_length

    def _iter_stitches_between_positions(
        self, position_1: Vec2D, position_2: Vec2D
    ) -> Generator[tuple[StitchCommand, float, float], None, None]:
        # Running stitch between two points, stopping exactly at position 2 and not
        # adding any stitch at position 1. The final stitch will be between 0.5 and 1.5
        # times the stitch length.
        x, y = position_1
        x_end, y_end = position_2

        distance = math.sqrt((x - x_end) ** 2 + (y - y_end) ** 2)
        angle = math.atan2(y_end - y, x_end - x)
        dx = math.cos(angle)
        dy = math.sin(angle)

        # First, the needle does stitches until the distance to the end-point is
        # less than two stitch-lengths away
        distance_traveled = 0
        while distance_traveled + 2 * self.stitch_length < distance:
            x += self.stitch_length * dx
            y += self.stitch_length * dy
            distance_traveled += self.stitch_length
            yield x, y, pyembroidery.STITCH

        # Then, we check if we need one final stitch, to prevent stitches larger than
        # 1.5 times the stitch length
        if distance - distance_traveled >= 1.5 * self.stitch_length:
            x += self.stitch_length * dx
            y += self.stitch_length * dy
            distance_traveled += self.stitch_length
            yield x, y, pyembroidery.STITCH

        # We add the final stitch at the end-point, which is guaranteed to be at most
        # 1.5 and at least 0.5 stitch-lengths away from the second to last stitch.
        yield x_end, y_end, pyembroidery.STITCH

    def _get_stitch_commands(self) -> list[tuple[float, float, StitchCommand]]:
        if not self._positions:
            return []

        stitch_commands = [(self._start_pos[0], self._start_pos[1], pyembroidery.STITCH)]
        stitch_commands.extend(self._iter_stitches_between_positions(self._start_pos, self._positions[0]))
        for pos1, pos2 in itertools.pairwise(self._positions):
            stitch_commands.extend(self._iter_stitches_between_positions(pos1, pos2))

        return stitch_commands


def iterate_back_and_forth(iterable: Iterable[Any]) -> Generator[tuple[StitchCommand, float, float], None, None]:
    """Iterates back and forth trough an iterable

    Each element (except the first) is given twice, with the previous element sandwiched inbetween.
    (So all element exept he first and last is given in total three times)

    Parameters
    ----------
    iterable
        Iterable to iterate back and forth over


    Yields
    ------
    Elements from the iterable

    >>> list(iterate_back_and_forth([0, 1, 2, 3]))
    [0, 1, 0, 1, 2, 1, 2, 3, 2, 3]
    """
    iterator = iter(iterable)
    previous = next(iterator)
    yield previous

    for item in iterator:
        yield item
        yield previous
        yield item
        previous = item


class TripleStitch(StitchGroup):
    """Stitch group for triple stitches.

    TripleStitch is the same as a :py:class:`RunningStitch`, but the thread moves back and forth three times for each
    stitch.

    Parameters
    ----------
    stitch_length : int
        Number of steps between each stitch.
    """

    def __init__(self, start_pos: Vec2D, color: str, stitch_length: float) -> None:
        super().__init__(start_pos=start_pos, color=color)
        self.running_stitch = RunningStitch(start_pos=start_pos, stitch_length=stitch_length, color=color)

    def _get_stitch_commands(self) -> list[tuple[float, float, StitchCommand]]:
        self.running_stitch._positions = self._positions
        stitch_commands = self.running_stitch._get_stitch_commands()

        return list(iterate_back_and_forth(stitch_commands))


class JumpStitch(StitchGroup):
    """Stitch group for jump stitches.

    A jump stitch group always starts with a trim command followed by the needle moving without sewing any stitches.

    See :py:class:`StitchGroup` for more information on stitch groups.

    Parameters
    ----------
    skip_intermediate_jumps : bool (optional, default=True)
        If True, then multiple jump commands will be collapsed into one jump command. This is useful in the cases
        where there may be multiple subsequent jumps with no stitches inbetween. Multiple subsequent jumps doesn't
        make sense but it can happen dependent on how you generate your patterns.
    """

    def __init__(self, start_pos: Vec2D, color:str=None, skip_intermediate_jumps: bool = True) -> None:
        super().__init__(start_pos=start_pos, color=color) 
        self.skip_intermediate_jumps = skip_intermediate_jumps

    def _get_stitch_commands(self) -> list[tuple[float, float, StitchCommand]]:
        if not self._positions:
            return []

        stitch_commands = [(self._start_pos[0], self._start_pos[1], pyembroidery.TRIM)]
        if self.skip_intermediate_jumps:
            x, y = self._positions[-1]
            stitch_commands.append((x, y, pyembroidery.JUMP))
            return stitch_commands

        for x, y in self._positions:
            stitch_commands.append((x, y, pyembroidery.JUMP))
        return stitch_commands


class ZigzagStitch(UnitStitch):
    def __init__(
        self,
        start_pos: Vec2D,
        color: str, 
        stitch_length: int | float,
        stitch_width: int | float,
        center: bool = False,
        auto_adjust: bool = True,
        enforce_end_stitch: bool = True,
        enforce_start_stitch: bool = True) -> None:
        
        super().__init__(
            start_pos=start_pos,
            color=color, 
            stitch_length=stitch_length,
            auto_adjust=auto_adjust,
            enforce_end_stitch=enforce_end_stitch,
            enforce_start_stitch=enforce_start_stitch
            )

        self.center = center
        self.stitch_width = stitch_width
        self.stitch_stop_multiplier = 1 # Apparently if you use the <= operator in the while loop in the iter part it works without if?
        # if self.center:
        #     self.stitch_stop_multiplier = 1
        # else:
        #     self.stitch_stop_multiplier = 1

    def _stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float) -> list[tuple[float, float, StitchCommand]]:
        """Stitch a single zigzag. We stitch right, then left.
        The right stitch is one stitch_width to the right of the left stitch.
        """
        x = start_pos[0]
        y = start_pos[1]
        dx = math.cos(angle)
        dy = math.sin(angle)

        # Right Stitch
        x += stitch_length*0.5 * dx
        y += stitch_length*0.5 * dy
        
        right_angle = angle - math.pi/2
        stitch_x = x + (self.stitch_width * math.cos(right_angle))
        stitch_y = y + (self.stitch_width * math.sin(right_angle))
        yield stitch_x, stitch_y, pyembroidery.STITCH

        # Left Stitch
        x += stitch_length*0.5 * dx
        y += stitch_length*0.5 * dy
        yield x, y, pyembroidery.STITCH

    def _start_stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float) -> list[tuple[float, float, StitchCommand]]:
        """If center, move 1/4 of stitch length forward, and half a stitch width to the left."""
        if self.center:
            self.x += stitch_length*0.25 * math.cos(angle)
            self.y += stitch_length*0.25 * math.sin(angle)
            left_angle = angle + math.pi/2 

            self.x += (self.stitch_width/2 * math.cos(left_angle)) 
            self.y += (self.stitch_width/2 * math.sin(left_angle))
            self.distance_traveled += stitch_length*0.25

            yield self.x, self.y, pyembroidery.STITCH

    def _end_stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float, distance: float) -> list[tuple[float, float, StitchCommand]]:
        """We have two cases to consider:

        1. The end-point is after the next stitch of the zigzag. In this case, we will have to draw that next stitch.
        We can tell if this is the case if the distance to the end == 0.75 * stitch_length

        2. The end-point is immediately after the current stitch of the zigzag. In this case, immediately draw the end stitch. 
        We can tell if this is the case if the distance to the end == 0.25 * stitch_length
        """
        if self.center:
            if distance > 0.5 * stitch_length:
                # Case 1 - Yield next stitch, then final stitch
                self.x += stitch_length*0.5 * math.cos(angle)
                self.y += stitch_length*0.5 * math.sin(angle)
                right_angle = angle - math.pi/2 

                self.x += (self.stitch_width * math.cos(right_angle)) 
                self.y += (self.stitch_width * math.sin(right_angle))
                self.distance_traveled += stitch_length*0.5
                
                yield self.x, self.y, pyembroidery.STITCH

                # Now we skip to end position
                # Cheat by knowing that they will put a stitch at the end position
                # Hence we dont need to do anything

                # Do not yield a stitch at the end position
                pass
            else:
                # Case 2 - Skip to final stitch
                # Cheat by knowing that they will put a stitch at the end position
                # Hence we dont need to do anything

                # self.x += stitch_length*0.25 * math.cos(angle)
                # self.y += stitch_length*0.25 * math.sin(angle)
                # right_angle = angle - math.pi/2 

                # self.x += (self.stitch_width/2 * math.cos(right_angle)) 
                # self.y += (self.stitch_width/2 * math.sin(right_angle))
                # self.distance_traveled += stitch_length*0.25
                
                # # Do not yield a stitch at the end position
                pass


class SatinStitch(ZigzagStitch):
    """Stitch group for satin stitches.
    A satin stitch is simply a zigzag stitch with a tight density. This creates a solid fill.
    We use 0.3mm for the density."""
    speedup=1
    
    def __init__(self, start_pos: Vec2D, color: str, stitch_width: int | float, center: bool = True) -> None:
        super().__init__(start_pos=start_pos, color=color, stitch_width=stitch_width, stitch_length=3, center=center)
    

class CrossStitch(UnitStitch):
    def __init__(
        self,
        start_pos: Vec2D,
        color: str, 
        stitch_length: int | float,
        stitch_width: int | float,
        center: bool = False,
        auto_adjust: bool = True,
        enforce_end_stitch: bool = True,
        enforce_start_stitch: bool = True) -> None:
        
        super().__init__(
            start_pos=start_pos,
            color=color, 
            stitch_length=stitch_length,
            auto_adjust=auto_adjust,
            enforce_end_stitch=enforce_end_stitch,
            enforce_start_stitch=enforce_start_stitch
            )

        self.center = center
        self.stitch_width = stitch_width

        if auto_adjust:
            self.stitch_stop_multiplier = 0
        else:
            self.stitch_stop_multiplier = 1
    def _stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float) -> list[tuple[float, float, StitchCommand]]:
        """The cross stitch is implemented by going from the top left corner to the bottom right corner, then moving
        from the bottom right to the bottom left, before finally going to the top right corner. This corner will
        be the top left of the next cross stitch."""
        x = start_pos[0]
        y = start_pos[1]
        dx = math.cos(angle)
        dy = math.sin(angle)

        # TOP LEFT TO BOTTOM RIGHT

        # Top-Left to Top-Right
        x += stitch_length * dx 
        y += stitch_length * dy
        # Top-Right to Bottom-Right
        right_angle = angle - math.pi/2 # Turn right 90 degrees
        x += self.stitch_width * math.cos(right_angle)
        y += self.stitch_width * math.sin(right_angle)
        yield x, y, pyembroidery.STITCH

        # BOTTOM RIGHT TO BOTTOM LEFT 
        reverse_angle = angle + math.pi # Turn 180 degrees
        x -= stitch_length * dx 
        y -= stitch_length * dy
        yield x, y, pyembroidery.STITCH

        # BOTTOM LEFT TO TOP RIGHT
        
        # Bottom-Left to Top-Left
        left_angle = angle + math.pi/2 # Turn left 90 degrees 
        x += self.stitch_width * math.cos(left_angle)
        y += self.stitch_width * math.sin(left_angle)
        # Top-Left to Top-Right
        x += stitch_length * dx 
        y += stitch_length * dy
        yield x, y, pyembroidery.STITCH

    def _start_stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float) -> list[tuple[float, float, StitchCommand]]:
        """If center, move 1/2 of stitch width to the left."""
        if self.center:
            left_angle = angle + math.pi/2
            self.x += (self.stitch_width/2 * math.cos(left_angle))
            self.y += (self.stitch_width/2 * math.sin(left_angle))
            yield self.x, self.y, pyembroidery.STITCH

    def _end_stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float, distance: float) -> list[tuple[float, float, StitchCommand]]:
        """If center, we move 1/2 of stitch width back to the right."""
        if self.center:
            right_angle = angle - math.pi/2
            self.x += (self.stitch_width/2 * math.cos(right_angle))
            self.y += (self.stitch_width/2 * math.sin(right_angle))
            yield self.x, self.y, pyembroidery.STITCH


class ZStitch(UnitStitch):
    def __init__(
        self,
        start_pos: Vec2D,
        color: str, 
        stitch_length: int | float,
        stitch_width: int | float,
        center: bool = False,
        auto_adjust: bool = True,
        enforce_end_stitch: bool = True,
        enforce_start_stitch: bool = True) -> None:
        
        super().__init__(
            start_pos=start_pos,
            color=color, 
            stitch_length=stitch_length,
            auto_adjust=auto_adjust,
            enforce_end_stitch=enforce_end_stitch,
            enforce_start_stitch=enforce_start_stitch
            )

        self.center = center
        self.stitch_width = stitch_width

        self.stitch_stop_multiplier = 1

    def _stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float) -> list[tuple[float, float, StitchCommand]]:
        """In Z-stitch, we stitch forward by stitch_length and right by stitch_width, then back left by stitch_width."""
        x = start_pos[0]
        y = start_pos[1]
        dx = math.cos(angle)
        dy = math.sin(angle)

        # Diagonal stitch
        x += stitch_length * dx
        y += stitch_length * dy
        right_angle = angle - math.pi/2
        stitch_x = x + (self.stitch_width * math.cos(right_angle))
        stitch_y = y + (self.stitch_width * math.sin(right_angle))
        yield stitch_x, stitch_y, pyembroidery.STITCH

        # Up stitch
        # We are already in the correct position!
        yield x, y, pyembroidery.STITCH

    def _start_stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float) -> list[tuple[float, float, StitchCommand]]:
        """If center, we move 1/2 stitch_width to the right and 1/2 stitch_length forward, then one stitch_width left, to simulate half a stitch"""
        if self.center:
            
            self.x += (self.stitch_length/2 * math.cos(angle))
            self.y += (self.stitch_length/2 * math.sin(angle))

            right_angle = angle - math.pi/2
            self.x += (self.stitch_width/2 * math.cos(right_angle))
            self.y += (self.stitch_width/2 * math.sin(right_angle))
            yield self.x, self.y, pyembroidery.STITCH

            left_angle = angle + math.pi/2
            self.x += (self.stitch_width * math.cos(left_angle))
            self.y += (self.stitch_width * math.sin(left_angle))
            yield self.x, self.y, pyembroidery.STITCH
    
    def _end_stitch_unit(self, start_pos: Vec2D, angle: float, stitch_length: float, distance: float) -> list[tuple[float, float, StitchCommand]]:
        """If center, we need to have half a diagonal stitch to return to the original position along the direction of travel."""
        # Since the final stitch is automatically drawn, we do not need to do anything
        return iter(())


class DirectStitch(StitchGroup):
    """A minimal stitch just to run thread from one point to another."""

    def _iter_stitches_between_positions(
        self, position_1: Vec2D, position_2: Vec2D
    ) -> Generator[tuple[StitchCommand, float, float], None, None]:
        x, y = position_1
        x_end, y_end = position_2

        yield x_end, y_end, pyembroidery.STITCH

    def _get_stitch_commands(self) -> list[tuple[float, float, StitchCommand]]:
        if not self._positions:
            return []

        stitch_commands = [(self._start_pos[0], self._start_pos[1], pyembroidery.STITCH)]
        stitch_commands.extend(self._iter_stitches_between_positions(self._start_pos, self._positions[0]))
        for pos1, pos2 in itertools.pairwise(self._positions):
            stitch_commands.extend(self._iter_stitches_between_positions(pos1, pos2))

        return stitch_commands


class FastDirectStitch(DirectStitch):
    """A variation of direct stitch that will be fast when using fast_visualise """
    speedup = 2 
