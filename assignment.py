from __future__ import print_function
import time
from sr.robot import *

# Thresholds for controlling robot orientation and linear distance
ORIENTATION_THRESHOLD = 2.0
DISTANCE_THRESHOLD = 0.4

# Robot instance
robot = Robot()

# List to track grabbed boxes
grabbed_boxes = []

# Function to set linear velocity for a specified duration
def drive(speed, seconds):
    robot.motors[0].m0.power = speed
    robot.motors[0].m1.power = speed
    time.sleep(seconds)
    robot.motors[0].m0.power = 0
    robot.motors[0].m1.power = 0

# Function to set angular velocity for a specified duration, causing the robot to turn
def turn(speed, seconds):
    robot.motors[0].m0.power = speed
    robot.motors[0].m1.power = -speed
    time.sleep(seconds)
    robot.motors[0].m0.power = 0
    robot.motors[0].m1.power = 0

def find_closest_marker(marker_type, condition_func):
    min_distance = 100
    for box in robot.see():
        if (
            box.dist < min_distance
            and box.info.marker_type == marker_type
            and condition_func(box)
        ):
            min_distance = box.dist
            rot_y = box.rot_y
            code = box.info.code

    if min_distance == 100:
        return -1, -1, -1
    else:
        return min_distance, rot_y, code

def find_closest_gold():
    def condition(box):
        return box.info.code not in grabbed_boxes

    return find_closest_marker(MARKER_TOKEN_GOLD, condition)

def find_release_location():
    def condition(box):
        return box.info.code in grabbed_boxes

    return find_closest_marker(MARKER_TOKEN_GOLD, condition)


# Function to move the robot towards the closest golden box and stop when close enough to grab
def grab_gold():
    while True:
        dist, rot_y, code = find_closest_gold()

        if dist <= DISTANCE_THRESHOLD:
            print("Found a gold box!")
            break
        elif -ORIENTATION_THRESHOLD <= rot_y <= ORIENTATION_THRESHOLD:
            print("Moving forward.")
            drive(15, 0.33)
        elif rot_y < -ORIENTATION_THRESHOLD:
            print("Adjusting left.")
            turn(-3, 0.33)
        elif rot_y > ORIENTATION_THRESHOLD:
            print("Adjusting right.")
            turn(3, 0.33)

# Function to move towards the closest drop location and stop when close enough to release the box
def release_grabbed_gold():
    while True:
        dist, rot_y, code = find_release_location()

        if dist < DISTANCE_THRESHOLD + 0.2:
            print("Found a drop location!")
            break
        elif -ORIENTATION_THRESHOLD <= rot_y <= ORIENTATION_THRESHOLD:
            print("Moving forward.")
            drive(15, 0.33)
        elif rot_y < -ORIENTATION_THRESHOLD:
            print("Adjusting left.")
            turn(-3, 0.33)
        elif rot_y > ORIENTATION_THRESHOLD:
            print("Adjusting right.")
            turn(3, 0.33)

# Main algorithm
def main():
    # Initial search for golden boxes
    dist, rot_y, code = find_closest_gold()
    while dist == -1:
        print("Searching for a gold box...")
        turn(-10, 1)
        dist, rot_y, code = find_closest_gold()

    # Grab the first golden box
    grab_gold()
    robot.grab()
    print("Successfully grabbed the box.")

    # Move to drop location, release the box, and confirm delivery
    turn(-20, 0.6)
    drive(20, 10)
    robot.release()
    print("Package delivered.")

    # Avoid collisions and update the list of grabbed boxes
    drive(-15, 1.33)
    turn(-30, 1)
    grabbed_boxes.append(code)

    # Continue searching, grabbing, and dropping until all boxes are positioned together
    while len(grabbed_boxes) < 6:
        # Search for and grab the closest golden box
        dist, rot_y, code = find_closest_gold()
        while dist == -1:
            print("Searching for a gold box...")
            turn(-10, 1)
            dist, rot_y, code = find_closest_gold()
        grab_gold()
        robot.grab()
        print("Successfully grabbed the box.")

        # Find a drop location and release the box
        new_dist, new_rot_y, new_code = find_release_location()
        while new_dist == -1:
            print("Searching for a drop location...")
            turn(10, 1)
            new_dist, new_rot_y, new_code = find_release_location()
        release_grabbed_gold()
        robot.release()
        print("Package delivered.")
        drive(-15, 1.33)
        turn(-30, 1)

        # Add the code of the dropped box to the list
        grabbed_boxes.append(new_code)

main()

