import math
from abc import ABC, abstractmethod
from .base_turtle import Vec2D


def rotate_point(x, y, angle):
    """Rotate a point around the origin by a given angle (in radians)."""
    if x is not None and y is not None: # Not jump indicator
        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)
        x_new = x * cos_theta - y * sin_theta
        y_new = x * sin_theta + y * cos_theta
        return x_new, y_new
    else:
        return x, y

class Fill(ABC):
    """A class to represent a fill. This is a base class for other fill types.
    Given a list of points that make up a polygon, the fill() function should fill it in using the appropriate methods."""

    @abstractmethod
    def fill(self, points):
        raise NotImplementedError

class ScanlineFill(Fill):
    """The Scanline fill will create straight lines across the fill area to fill it up. Useful for small areas.

    Parameters
    ----------
    angle: str | int | float (default="auto")
        Angle of the lines, in radians. May also be the string 'auto'.
        If 'auto', the program will automatically try the angles of 0, 45, 90, and 135 degrees, to minimize the number of jump stitches.
    jump_at_edges: bool (default=False)
        If True, the fill will do a jump stitch when it encounters an edge during fill, such as to cross from one area to another.
        This creates a cleaner fill with less stray stitches.
        Set to False by default as this may slow down embroidery significantly, due to the number of jump stitches involved.
        """
    
    def __init__(self, angle : str | int | float = "auto", jump_at_edges : bool = False):
        if type(angle) == str and angle == "auto":
            self.auto = True
        else:
            self.auto = False
            self.angle = angle
        self.jump_at_edges = jump_at_edges
            
    def _fill_at_angle(self, turtle, points, angle, simulate=False):
        # Rotate the coordinates
        rot_points = []
        for x, y in points:
            x_rot, y_rot = rotate_point(x, y, angle)
            rot_points.append((x_rot, y_rot))

        # Find bounding box of polygon
        edges = []
        min_x = rot_points[0][0]
        max_x = rot_points[0][0]
        min_y = rot_points[0][1]
        max_y = rot_points[0][1]

        # Find all edges/segments that make up outline
        # After this, edges should be a list of ((x1, y1), (x2, y2)) tuples
        for i in range(len(rot_points) - 1):
            # If points is (None, None) ignore that edge! This separates different parts of the polygon.
            if rot_points[i][0] is None or rot_points[i + 1][0] is None:
                continue 
            edges.append((rot_points[i], rot_points[i + 1]))
            min_x = min(min_x, rot_points[i + 1][0])
            max_x = max(max_x, rot_points[i + 1][0])
            min_y = min(min_y, rot_points[i + 1][1])
            max_y = max(max_y, rot_points[i + 1][1])

        # Remove edges where p1 == p2
        edges_cleaned = []
        for edge in edges:
            if not (abs(edge[1][0] - edge[0][0]) < 1 and abs(edge[1][1] - edge[0][1]) < 1): 
                edges_cleaned.append(edge)
        edges = edges_cleaned


        # Sweep from +y to -y, populating a list of horizontal intersections at each y scanline
        scanned_lines = []
        scanline_y = min_y
        
        while scanline_y <= max_y:
            intersections = []
            for edge in edges:
                if edge[0][1] <= scanline_y <= edge[1][1] or edge[1][1] <= scanline_y <= edge[0][1]: 
                    if abs(edge[1][0] - edge[0][0]) > 1 and abs(edge[1][1] - edge[0][1]) > 1: # No horizontal and vertical edge
                        gradient =  (edge[1][0] - edge[0][0]) / (edge[1][1] - edge[0][1])
                        intersect_x = edge[0][0] + (scanline_y - edge[0][1]) * gradient
                        intersections.append((intersect_x, scanline_y))
                    elif abs(edge[1][0] - edge[0][0]) < 1: # x is equal, hence vertical edge
                        intersections.append((edge[0][0], scanline_y))
                    elif abs(edge[1][1] - edge[0][1]) < 1: # y is equal, hence horizontal edge
                        # We don't actually need to care about horiontal edges...?
                        continue
                        # intersections.append((edge[0][0], scanline_y))
                        # intersections.append((edge[1][0], scanline_y))
                    

            intersections.sort(key=lambda x: x[0])
            # Remove duplicates
            for i in range(len(intersections) - 1):
                if abs(intersections[i+1][0] - intersections[i][0]) < 1 and abs(intersections[i+1][1] - intersections[i][1]) < 1:
                    intersections[i] = None
            intersections = [x for x in intersections if x is not None]
            scanned_lines.append(intersections)
            scanline_y += 3 # 3 units (0.3mm) is the minimum density we use
            if scanline_y > max_y and scanline_y - max_y < 3 - 0.3: # Subtract 0.3 to prevent infinite loop when scanline_y == max_y
                scanline_y = max_y

        # Coordinates are still unrotated!

        jump_stitches = 0
        # Jump to start coordinate if needed
        start_idx = 0
        while len(scanned_lines[start_idx]) < 1:
            start_idx += 1

        start_pos_rot = rotate_point(scanned_lines[start_idx][0][0], scanned_lines[start_idx][0][1], -angle)

        if abs(Vec2D(start_pos_rot[0], start_pos_rot[1]) - turtle.pos()) > 1:
            with turtle.jump_stitch():
                jump_stitches += 1
                if not simulate: turtle.goto(start_pos_rot)

        # Continuously loop through scanned lines until there is nothing left to fill
        no_fill_in_current_iteration_flag = False
        while not no_fill_in_current_iteration_flag:
            no_fill_in_current_iteration_flag = True
            prev_line = None
            jump = False
            for i in range(start_idx, len(scanned_lines) - 1): # For each scanned line
                with turtle.fast_direct_stitch():
                    if len(scanned_lines[i]) >= 2: # If there are at least 2 coordinates, there needs to be a stitch between them!
                        no_fill_in_current_iteration_flag = False # Something was filled this iteration! For while loop to continue
                        stitch_rot = (
                            rotate_point(scanned_lines[i][0][0], scanned_lines[i][0][1], -angle), 
                            rotate_point(scanned_lines[i][1][0], scanned_lines[i][1][1], -angle)
                        )

                        if self.jump_at_edges:
                            # Check if the line will cross an edge, by seeing if previous stitch's left is 'lefter' than next stitch's right
                            # Check similarly for right hand side
                            if prev_line is not None and len(prev_line) >= 2:
                                if prev_line[1][0] < scanned_lines[i][0][0] or prev_line[0][0] > scanned_lines[i][1][0]:
                                    jump = True
                            prev_line = (scanned_lines[i][0], scanned_lines[i][1])

                        if jump: # If there are gaps in the scanned lines, jump to the position of the first stitch
                            with turtle.jump_stitch():
                                if not simulate: turtle.goto(stitch_rot[0])
                                jump_stitches += 1
                                jump = False
                        if not simulate: turtle.goto(stitch_rot[0])
                        if not simulate: turtle.goto(stitch_rot[1])
                        scanned_lines[i].pop(0)
                        scanned_lines[i].pop(0)
                    else:
                        jump = True

        return jump_stitches
    
    def fill(self, turtle, points):
        assert len(points)>0, "'points' cannot be an empty list! (in ScanlineFill)"
        if not self.auto:
            self._fill_at_angle(turtle, points, self.angle)
        else:
            best_angle = 0
            min_jumps = self._fill_at_angle(turtle, points, best_angle, simulate=True)
            for angle in (math.pi/4, math.pi/2, 3*math.pi/4):
                jumps = self._fill_at_angle(turtle, points, angle, simulate=True)
                if jumps < min_jumps:
                    min_jumps = jumps
                    best_angle = angle

            self._fill_at_angle(turtle, points, best_angle)

        

 
                        
                        
            
