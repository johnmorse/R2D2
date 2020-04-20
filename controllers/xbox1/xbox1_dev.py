#!/usr/bin/python
""" XBOX1 Joystick controller MUST RUN WITH !!SUDO!! """
#from __future__ import print_function
#from future import standard_library
#standard_library.install_aliases()
from builtins import str
from builtins import range
import pygame
#import requests
#import csv
#import configparser
import os
import sys
import time
import math
import datetime
#import argparse
from io import StringIO
#from collections import defaultdict
#from shutil import copyfile
#import odrive
#import signal
#import SabertoothPacketSerial
#sys.path.insert(0, '/home/pi/r2_control')
#from r2utils import telegram, internet, mainconfig

BUT_A   =  0
BUT_B   =  1
#       =  2
BUT_X   =  3
BUT_Y   =  4
#       =  5
BUT_TL  =  6
BUT_TR  =  7
#       =  8
#       =  9
#       = 10
BUT_MEN = 11
#       = 12
BUT_LJS = 13
BUT_RJS = 14

def printButtonEvent(event):
    if event.button == BUT_A:
        print("A")
    elif event.button == BUT_B:
        print("B")
    elif event.button == BUT_X:
        print("X")
    elif event.button == BUT_Y:
        print("Y")
    elif event.button == BUT_TL:
        print("Top left button")
    elif event.button == BUT_TR:
        print("Top right button")
    elif event.button == BUT_MEN:
        print("Menu")
    elif event.button == BUT_LJS:
        print("Left joystick click")
    elif event.button == BUT_RJS:
        print("Right joystick click")
    else:
        print "Unknown button"
        print(event)

pygame.display.init()

while True:
    pygame.joystick.quit()
    pygame.joystick.init()
    num_joysticks = pygame.joystick.get_count()
    print("Waiting for joystick... (count: %s)" % num_joysticks)
    if num_joysticks != 0:
        break
    time.sleep(5)

pygame.init()
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print("Framebuffer size: %d x %d" % (size[0], size[1]))

j = pygame.joystick.Joystick(0)
j.init()
buttons = j.get_numbuttons()

print("Joystick buttons(%d)" % (buttons))
last_command = time.time()
joystick = True

previous = ""
_throttle = 0
_turning = 0

speed_fac = 0

# Main loop
while (joystick):
    if os.path.exists('/dev/input/js0') == False:
        joystick = False
        continue
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.JOYBUTTONUP:
            # Ignore button up events, just track button down for now
            continue
        if event.type == pygame.JOYBUTTONDOWN:
            printButtonEvent(event)
            buf = StringIO()
            for i in range(buttons):
                button = j.get_button(i)
                buf.write(str(button))
            combo = buf.getvalue()
            print("Buttons pressed: %s" % combo)
            if event.button == 11:
                joystick = False
                continue
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 0: # Left axis vertial
                print("Value (Drive): %s : Speed Factor : %s" % (event.value, speed_fac))
            elif event.axis == 1: # Left axis horizontal
                print("Value (Steer): %s" % event.value);
            elif event.axis == 2: # Right axis vertical
                print("Right joystic vertical: %s" % event.value)
            elif event.axis == 3: # Right axis horizontal
                print("Value (Dome): %s" % event.value)
            elif event.axis == 4:
                print("Right trigger")
            elif event.axis == 5: # Right axis horizontal
                print("Left trigger")
            else:
                print("JOYAXISMOTION  event.axis: %s" % event.axis)
        elif event.type == pygame.JOYHATMOTION:
            lpad = event.value[0] < 0;
            rpad = event.value[0] > 0;
            dpad = event.value[1] < 0;
            upad = event.value[1] > 0;
            if not (lpad | rpad | dpad | upad):
                print("D-pad all buttons are now up")
            elif lpad and upad:
                print("D-pad left/up")
            elif lpad and dpad:
                print("D-pad left/down")
            elif dpad and rpad:
                print("D-pad right/down")
            elif rpad and upad:
                print("D-pad right/up")
            elif lpad:
                print("D-pad left")
            elif rpad:
                print("D-pad right")
            elif upad:
                print("D-pad up")
            elif dpad:
                print("D-pad down")
            else:
                print("pygame.JOYHATMOTION value:%s" % event.value)
        else:
            print(event)
