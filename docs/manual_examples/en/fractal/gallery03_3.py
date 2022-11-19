from turtlethread import Turtle

def draw_arm(needle, length, rekursion_level):
    if rekursion_level == 0:
        needle.forward(length)
    elif rekursion_level % 2 == 0:
        # Move forward a little bit
        draw_arm(needle, 0.4*length, rekursion_level-1)

        # Draw the first "branch" pointing a little downwards
        needle.right(45)
        draw_arm(needle, length*0.3, rekursion_level-1)
        needle.backward(length*0.3)
        needle.left(45)
        # Draw the second "branch" pointing a little upwards
        needle.left(45)
        draw_arm(needle, length*0.3, rekursion_level-1)
        needle.backward(length*0.3)
        needle.right(45)

        # Move forward a little bit
        draw_arm(needle, length*0.6, rekursion_level-1)
    else:
        # Move forward a little bit
        draw_arm(needle, 0.4*length, rekursion_level-1)

        # Draw the first "branch" pointing a little downwards
        needle.right(60)
        draw_arm(needle, length*0.2, rekursion_level-1)
        needle.backward(length*0.2)
        needle.left(60)
        # Draw the second "branch" pointing a little upwards
        needle.left(60)
        draw_arm(needle, length*0.2, rekursion_level-1)
        needle.backward(length*0.2)
        needle.right(60)
        
        draw_arm(needle, 0.2*length, rekursion_level-1)

        # Draw the third "branch" pointing a little downwards
        needle.right(60)
        draw_arm(needle, length*0.2, rekursion_level-1)
        needle.backward(length*0.2)
        needle.left(60)
        # Draw the fourth "branch" pointing a little upwards
        needle.left(60)
        draw_arm(needle, length*0.2, rekursion_level-1)
        needle.backward(length*0.2)
        needle.right(60)

        # Move forward a little bit
        draw_arm(needle, length*0.4, rekursion_level-1)

needle = Turtle()
with needle.running_stitch(50):
    for arm in range(6):
        draw_arm(needle, 400, 3)
        needle.backward(400)
        needle.right(60)

needle.visualise()