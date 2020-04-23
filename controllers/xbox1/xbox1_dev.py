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
import xbox1_defines
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

def printButtonEvent(event):
    if event.button == xbox1_defines.BUT_A:
        print("A")
    elif event.button == xbox1_defines.BUT_B:
        print("B")
    elif event.button == xbox1_defines.BUT_X:
        print("X")
    elif event.button == xbox1_defines.BUT_Y:
        print("Y")
    elif event.button == xbox1_defines.BUT_TOPL:
        print("Top left button")
    elif event.button == xbox1_defines.BUT_TOPR:
        print("Top right button")
    elif event.button == xbox1_defines.BUT_MENU:
        print("Menu")
    elif event.button == xbox1_defines.BUT_JOYSTL:
        print("Left joystick click")
    elif event.button == xbox1_defines.BUT_JOYSTR:
        print("Right joystick click")
    else:
        print "Unknown button"
        print(event)

def getButtonStateString(j, buttons):
    hat = j.get_hat(0)
    print(hat)
    buf = StringIO()
    for i in range(buttons):
        button = j.get_button(i)
        # Up
        if i == xbox1_defines.BUT_EMPTY4:
            if hat[1] > 0:
                button = 1
        # Down
        elif i == xbox1_defines.BUT_EMPTY5:
            if hat[1] < 0:
                button = 1
        # Left
        elif i == xbox1_defines.BUT_EMPTY7:
            if hat[0] < 0:
                button = 1
        # Right
        elif i == xbox1_defines.BUT_EMPTY8:
            if hat[0] > 0:
                button = 1
        buf.write(str(button))
    # Fill in the blank 0 to get to the last two postions
    dif = buttons - xbox1_defines.BUT_EMPTY7 - 1
    while dif > 0:
        buf.write('0')
        dif -= 1
    # Left
    if buttons <= xbox1_defines.BUT_EMPTY7:
        print("Left")
        button = 0;
        if hat[0] < 0:
            button = 1
        buf.write(str(button))
    # Right
    if buttons <= xbox1_defines.BUT_EMPTY8:
        button = 0;
        if hat[0] > 0:
            button = 1
        buf.write(str(button))
    return buf.getvalue()

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
hats = j.get_numhats()

print("Joystick buttons(%d) hats(%d)" % (buttons, hats))
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
            combo = getButtonStateString(j, buttons)
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
