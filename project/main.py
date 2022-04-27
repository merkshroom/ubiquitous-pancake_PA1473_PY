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
    "pink": (56, 19, 24),
    "center_colour": (15, 14, 9),
    "blue": (10, 23, 41),
    "green": (9, 32, 12),
    "purple": (12, 11, 31),
    "red": (None, None, None),
    "black": (5, 5, 5),
    "white": (60, 70, 70)
}

DRIVE_SPEED = 30
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
truckStatus = "drive"
current_colour = COLOURS["yellow"]

#ev3.reset()

def update_truck_status(status):
    global truckStatus
    if (status != truckStatus):
        truckStatus = status
        print(truckStatus)
        ev3.screen.print(truckStatus)
    return 0

def follow_line(colour) -> int:
    global colour_current
    global truckStatus
    distance_to_next = ultrasonic_sensor.distance()
    current_rgb_value = light_sensor.rgb()
    if distance_to_next > 120:
        if (abs((COLOURS[colour][0] - current_rgb_value[0])) < 5 and \
            abs((COLOURS[colour][1] - current_rgb_value[1])) < 5 and \
                abs((COLOURS[colour][2] - current_rgb_value[2])) < 5):
            robot.drive(DRIVE_SPEED, 0)
        else:
            colour_diffs = ((COLOURS[colour][0] - current_rgb_value[0]), (COLOURS[colour][1] - current_rgb_value[2]), (COLOURS[colour][2] - current_rgb_value[2]))
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
            crane_motor.run_time(LIFT_PALLET, PICKUP_TIME) # kolla senare vad det är
            failed_pick_up()
            done = True
        if(light_sensor.reflection() >= 50):
            update_truck_status("drive")
        robot.drive(-PICKUP_SPEED, 0)
        
        #crane_motor.run(-90)
    
    return 0

def pick_up_object_elevated() -> int:
    global done
    global craneUp

    if not front_button.pressed() and done == False:
        if craneUp == False:
            robot.stop()
            crane_motor.run_time(LIFT_ELEVATED_PALLET, PICKUP_TIME)
            craneUp = True
        robot.drive(PICKUP_SPEED, 0)
    else:
        if(done == False):
            robot.stop()
            crane_motor.run_time(LIFT_PALLET, PICKUP_TIME) # kolla senare vad det är
            failed_pick_up()
            done = True
        if(light_sensor.reflection() >= 50):
            crane_motor.run_time(-LIFT_ELEVATED_PALLET, PICKUP_TIME)
            update_truck_status("drive")
        robot.drive(-PICKUP_SPEED, 0)
        
        #crane_motor.run(-90)
    
    return 0

def failed_pick_up() -> int:
    if not front_button.pressed():
        print("failed to pick up an item")
    return 0

def change_colour(colour_current, colour_change) -> int:
    while colour_change != light_sensor.reflection():
        follow_line(colour_current)
    follow_line(colour_current)
    return colour_current

def leave_area() -> int:
    return 0

def return_to_area() -> int:
    return 0

def abort():
    robot.stop(10)
    if truckStatus == "elevated_pick_up":
        crane_motor.run_time(-LIFT_ELEVATED_PALLET, PICKUP_TIME)
        robot.drive(-PICKUP_SPEED, 0)
        return_to_area(COLOURS["center_colour"])
    elif truckStatus == "pick_up":
        crane_motor.run_time(-LIFT_PALLET, PICKUP_TIME)
        robot.drive(-PICKUP_SPEED, 0)
        return_to_area(COLOURS["center_colour"])
    else:
        return_to_area(COLOURS["center_colour"])
    
    return 0

if __name__ == "__main__":
    while True:
        print(truckStatus)
        while truckStatus == "drive":
            update_truck_status("drive")
            follow_line(current_colour)
            #print(light_sensor.reflection())
            if(light_sensor.reflection() >= 50):
                update_truck_status("elevated_pick_up")
        while truckStatus == "pick_up":
            #update_truck_status("pick_up")
            pick_up_object()
        while truckStatus == "elevated_pick_up":
            pick_up_object_elevated()
        while truckStatus == "leave":
            update_truck_status("leave")
            leave_area()
        while truckStatus == "return_area":
            update_truck_status(return_area)
            return_to_area()