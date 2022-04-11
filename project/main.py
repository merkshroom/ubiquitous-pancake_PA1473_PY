#!/usr/bin/env pybricks-micropython
import sys
import __init__

import time
from pybricks import robotics
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

Left_drive=Port.C 
Right_drive=Port.B
Crane_motor=Port.A
Front_button=Port.S1
Light_sensor=Port.S3
Ultrasonic_sensor=Port.S4

ev3 = EV3Brick()


truckStatus = None
def updateTruckStatus(status):
    if (status != truckStatus):
        truckStatus = status
        print(truckStatus)
        ev3.screen.print(truckStatus)

def main():
    updateTruckStatus("Starting up")
    return 0

if __name__ == '__main__':
    sys.exit(main())
