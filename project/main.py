#!/usr/bin/env pybricks-micropython
import random
#import __init__
import time

from pybricks import robotics
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor, TouchSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

left_drive=Motor(Port.C, positive_direction = Direction.COUNTERCLOCKWISE, gears = [12, 20])
right_drive=Motor(Port.B, positive_direction = Direction.COUNTERCLOCKWISE, gears = [12, 20])
crane_motor=Motor(Port.A)
front_button= TouchSensor(Port.S1)
light_sensor= ColorSensor(Port.S3)
ultrasonic_sensor= UltrasonicSensor(Port.S4)
ev3 = EV3Brick()
robot = DriveBase(left_drive, right_drive, wheel_diameter=47, axle_track=128)

COLOURS = {
    "yellow": (None, None, None),
    "pink": (40, 16, 16),#old 56, 19, 24
    "center_colour": (15, 14, 9),
    "blue": (10, 23, 22),#old 10, 23, 41
    "green": (9, 32, 12),
    "purple": (12, 11, 31),
    "red": (None, None, None),
    "black": (5, 5, 5),
    "white": (60, 70, 70)
}

COLOUR_TOLERANCE = 5
DRIVE_SPEED = 20
PICKUP_SPEED = 15
PROPORTIONAL_GAIN = 2.5
PICKUP_TIME = 3000
LIFT_PALLET = 25
LIFT_ELEVATED_PALLET = 50
drive = True
pick_up = False
leave = False
done = False
craneUp = False
return_area = False
COLOUR_LST = [COLOURS["center_colour"], COLOURS["green"], COLOURS["black"]]
truck_status = "looking_for_colour"
current_colour = COLOUR_LST[0]
looking_for_colour = COLOURS["green"]
pick_up_colour = COLOURS["black"]


#ev3.reset()

def update_truck_status(status):
    global truck_status
    if (status != truck_status):
        truck_status = status
        print(truck_status)
        ev3.screen.print(truck_status)
    return 0

def follow_line() -> int:
    global truck_status
    global current_colour
    global looking_for_colour

    distance_to_next = ultrasonic_sensor.distance()
    current_rgb_value = light_sensor.rgb()
    if (truck_status == "looking_for_colour" and \
    abs((looking_for_colour[0] - current_rgb_value[0])) < COLOUR_TOLERANCE and \
    abs((looking_for_colour[1] - current_rgb_value[1])) < COLOUR_TOLERANCE and \
    abs((looking_for_colour[2] - current_rgb_value[2])) < COLOUR_TOLERANCE):
        print("hello")
        robot.straight(-25) #Needs changing to values that work better
        robot.turn(75) #Needs changing to values that work better
        current_colour = looking_for_colour
        truck_status = "drive"
        ev3.screen.print("left the area")
        

    if distance_to_next > 250:
        if (abs((current_colour[0] - current_rgb_value[0])) < COLOUR_TOLERANCE and \
            abs((current_colour[1] - current_rgb_value[1])) < COLOUR_TOLERANCE and \
            abs((current_colour[2] - current_rgb_value[2])) < COLOUR_TOLERANCE):
            robot.drive(DRIVE_SPEED, 60)
        else:
            colour_diffs = ((current_colour[0] - current_rgb_value[0]), (current_colour[1] - current_rgb_value[2]), (current_colour[2] - current_rgb_value[2]))
            deviation_angle = 10 - (((current_rgb_value[0] + current_rgb_value[1] + current_rgb_value[2]) / 3) - ((colour_diffs[0] + colour_diffs[1] + colour_diffs[2]) / 3)) / 5
            turn_rate = PROPORTIONAL_GAIN * deviation_angle
            robot.drive(DRIVE_SPEED, turn_rate)
    else:
        robot.stop()
        wait(10)
    return 0

def pick_up_object() -> int:
    global done

    if not front_button.pressed() and done == False:
        robot.drive(PICKUP_SPEED, 0)
    else:
        if(done == False):
            robot.stop()
            crane_motor.run_time(-LIFT_PALLET, PICKUP_TIME) # kolla senare vad det är
            #failed_pick_up()
            update_truck_status("drive")
            done = True
    return 0

def pick_up_object_elevated() -> int:
    global done
    global craneUp

    if not front_button.pressed() and done == False:
        if craneUp == False:
            robot.stop()
            crane_motor.run_time(-LIFT_ELEVATED_PALLET, PICKUP_TIME)
            craneUp = True
        robot.drive(PICKUP_SPEED, 0)
    else:
        if(done == False):
            robot.stop()
            crane_motor.run_time(-LIFT_PALLET, PICKUP_TIME) # kolla senare vad det är
            done = True
        if done == True:
            
            crane_motor.run_time(-LIFT_ELEVATED_PALLET, PICKUP_TIME)
            robot.straight(-100)
            crane_motor.run_time(LIFT_PALLET, PICKUP_TIME)
            update_truck_status("drive")
    return 0

def failed_pick_up() -> int:
    if not front_button.pressed():
        print("failed to pick up an item")
    return 0

def emergency_mode():
    if not front_button.pressed():
        print("Dropped item")
        robot.stop()

def change_colour(new_colour) -> int:
    global truck_status
    global looking_for_colour
    truck_status = "looking_for_colour"
    looking_for_colour = new_colour

def leave_area() -> int:
    return 0

def return_to_area() -> int:
    return 0

def abort():
    robot.stop(10)
    if truck_status == "elevated_pick_up":
        crane_motor.run_time(-LIFT_ELEVATED_PALLET, PICKUP_TIME)
        robot.drive(-PICKUP_SPEED, 0)
        return_to_area(COLOURS["center_colour"])
    elif truck_status == "pick_up":
        crane_motor.run_time(-LIFT_ELEVATED_PALLET, PICKUP_TIME)
        robot.drive(-PICKUP_SPEED, 0)
        return_to_area(COLOURS["center_colour"])
    else:
        return_to_area(COLOURS["center_colour"])
    
    return 0

has_changed_colour = False #Just for testing the change_colour function and updated follow_line
watch = StopWatch()

if __name__ == "__main__":
    while True:
        if watch.time() > 2000 and has_changed_colour == False: #Just for testing the change_colour function and updated follow_line
            change_colour(COLOUR_LST[1])
            has_changed_colour = True

        print(truck_status)
        while truck_status == "drive" or truck_status == "looking_for_colour":
            
            if Button.CENTER in ev3.buttons.pressed() :
                robot.stop()
                wait(50000)
            
            #looking_for_colour = input()
            follow_line()
            current_rgb_value = light_sensor.rgb()

            # Changes colour when previous colour is found
            if ( \
                abs((COLOUR_LST[1][0] - current_rgb_value[0])) < COLOUR_TOLERANCE and \
                abs((COLOUR_LST[1][1] - current_rgb_value[1])) < COLOUR_TOLERANCE and \
                abs((COLOUR_LST[1][2] - current_rgb_value[2])) < COLOUR_TOLERANCE):
                change_colour(COLOUR_LST[2])

            if ( \
                abs((pick_up_colour[0] - current_rgb_value[0])) < COLOUR_TOLERANCE and \
                abs((pick_up_colour[1] - current_rgb_value[1])) < COLOUR_TOLERANCE and \
                abs((pick_up_colour[2] - current_rgb_value[2])) < COLOUR_TOLERANCE):
                truck_status = "pick_up"

        while truck_status == "pick_up":
            if Button.CENTER in ev3.buttons.pressed() :
                robot.stop()
                wait(50000)
             #update_truck_status("pick_up")
            pick_up_object()
        while truck_status == "pick_up":
            if Button.CENTER in ev3.buttons.pressed():
                robot.stop()
                wait(50000)
            pick_up_object_elevated()
        while truck_status == "leave":
            if Button.CENTER in ev3.buttons.pressed():
                robot.stop()
                wait(50000)
            update_truck_status("leave")
            leave_area()
        while truck_status == "return_area":
            if Button.CENTER in ev3.buttons.pressed():
                robot.stop()
                wait(50000)
            update_truck_status("return_area")
            return_to_area()