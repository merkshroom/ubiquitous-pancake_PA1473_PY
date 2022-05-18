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

ev3 = EV3Brick()
left_drive=Motor(Port.C, positive_direction = Direction.COUNTERCLOCKWISE, gears = [12, 20])
right_drive=Motor(Port.B, positive_direction = Direction.COUNTERCLOCKWISE, gears = [12, 20])
robot = DriveBase(left_drive, right_drive, wheel_diameter=47, axle_track=128)

crane_motor=Motor(Port.A)
front_button= TouchSensor(Port.S1)
light_sensor= ColorSensor(Port.S3)
ultrasonic_sensor= UltrasonicSensor(Port.S4)

COLOURS = {
    "yellow": (83, 52, 21),
    "pink": (40, 16, 16), #old 56, 19, 24
    "center_colour": (15, 14, 9),
    "blue": (10, 23, 22), #old 10, 23, 41
    "green": (9, 32, 12),
    "purple": (12, 11, 31),
    "red": (None, None, None),
    "black": (5, 5, 5),
    "white": (60, 70, 70)
}
COLOUR_LST = [COLOURS["center_colour"], COLOURS["green"], COLOURS["black"]]

COLOUR_TOLERANCE = 5
DRIVE_SPEED = 20
PICKUP_SPEED = 15
PROPORTIONAL_GAIN = 2.5
PICKUP_TIME = 3000
LIFT_PALLET = 25
LIFT_ELEVATED_PALLET = 30

current_colour = COLOUR_LST[0]
looking_for_colour = COLOURS["green"]
pick_up_colour = COLOURS["black"]

truck_status = "drive"


def update_truck_status(status):
    global truck_status
    if (status != truck_status):
        truck_status = status
        print(truck_status)
        ev3.screen.print(truck_status)

def follow_line():
    global truck_status
    global current_colour
    global looking_for_colour

    distance_to_next = ultrasonic_sensor.distance()
    current_rgb_value = light_sensor.rgb()
    if (truck_status == "looking_for_colour" and \
    abs((looking_for_colour[0] - current_rgb_value[0])) < COLOUR_TOLERANCE and \
    abs((looking_for_colour[1] - current_rgb_value[1])) < COLOUR_TOLERANCE and \
    abs((looking_for_colour[2] - current_rgb_value[2])) < COLOUR_TOLERANCE):
        robot.straight(-25)
        robot.turn(75)
        current_colour = looking_for_colour
        print(current_colour)
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

def pick_up_object():
    pick_up_completed = False

    if front_button.pressed() and not pick_up_completed:
        robot.stop()
        crane_motor.run_time(LIFT_PALLET, PICKUP_TIME, Stop.HOLD,True) # kolla senare vad det är
        pick_up_completed = True
    elif pick_up_completed:
        robot.straight(-100)
        if not front_button.pressed():
            emergency_mode()
        else:
            update_truck_status("drive")
    else:
        robot.drive(PICKUP_SPEED, 0)

def pick_up_object_elevated():
    craneUp = False
    epu_completed = False

    if front_button.pressed() and not epu_completed:
        robot.stop()
        crane_motor.run_time(LIFT_PALLET, PICKUP_TIME) # kolla senare vad det är
        epu_completed = True
    elif epu_completed:
        crane_motor.run_time(LIFT_ELEVATED_PALLET, PICKUP_TIME)
        robot.straight(-100)
        crane_motor.run_time(-LIFT_PALLET, PICKUP_TIME)
        if not front_button.pressed():
            emergency_mode()
        else:
            update_truck_status("drive")
    else:
        if not craneUp:
            robot.stop()
            crane_motor.run_time(LIFT_ELEVATED_PALLET, PICKUP_TIME)
            craneUp = True
        robot.drive(PICKUP_SPEED, 0)

def failed_pick_up():
    if not front_button.pressed():
        print("failed to pick up an item")

def emergency_mode():
    crane_motor.run_target(-30, 0)
    ev3.speaker.say("Emergency mode")
    update_truck_status("stopped")

def change_colour(new_colour):
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
    

def manual_stop():
    robot.stop()
    update_truck_status("stopped")
    print("Truck has been manually stopped")
    ev3.screen.print("Truck has been manually stopped")
    ev3.speaker.say("Manually stopped")


if __name__ == "__main__":
    while True:

        while truck_status == "drive" or truck_status == "looking_for_colour":
            if Button.CENTER in ev3.buttons.pressed() :
                manual_stop()
            
            follow_line()

            # Changes colour when previous colour is found
            current_rgb_value = light_sensor.rgb()
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
                manual_stop()
            pick_up_object()
        while truck_status == "pick_up":
            if Button.CENTER in ev3.buttons.pressed() :
                manual_stop()
            pick_up_object_elevated()
        while truck_status == "leave":
            if Button.CENTER in ev3.buttons.pressed() :
                manual_stop()
            update_truck_status("leave")
            leave_area()
        while truck_status == "return_area":
            if Button.CENTER in ev3.buttons.pressed() :
                manual_stop()
            update_truck_status("return_area")
            return_to_area()