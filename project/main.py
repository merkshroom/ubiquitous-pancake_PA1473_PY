#!/usr/bin/env pybricks-micropython
import random
import __init__
import time

from pybricks import robotics
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

left_drive=Port.C 
right_drive=Port.B
crane_motor=Port.A
front_button=Port.S1
light_sensor=Port.S3
ultrasonic_sensor=Port.S4
ev3 = EV3Brick()

BLACK = 10
WHITE = 40
DRIVE_SPEED = 60
PROPORTIONAL_GAIN = 2.5
drive = True
pick_up = False
leave = False
return_area = False
truckStatus = None
threshold_angle = (BLACK + WHITE) / 2

ev3.reset()

def update_truck_status(status) -> int:
    if (status != truckStatus):
        truckStatus = status
        print(truckStatus)
        ev3.screen.print(truckStatus)
    return 0

def follow_line() -> int:
    distance_to_next = ultrasonic_sensor.distance()
    if distance_to_next > 120:
        deviation_angle = light_sensor.reflection() - threshold_angle
        turn_rate = PROPORTIONAL_GAIN * deviation_angle
        ev3.drive(DRIVE_SPEED, turn_rate)
    else:
        ev3.stop()
        wait(10)
    return 0

def pick_up_object() -> int:
    return 0

def leave_area() -> int:
    return 0

def return_to_area() -> int:
    return 0

if __name__ == "__main__":
    while True:
        while drive == True:
            update_truck_status(drive)
            follow_line()
        while pick_up == True:
            update_truck_status(pick_up)
            pick_up_object()
        while leave == True:
            update_truck_status(leave)
            leave_area()
        while return_area == True:
            update_truck_status(return_area)
            return_to_area()