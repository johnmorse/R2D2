#!/usr/bin/python
""" XBOX1 Joystick controller """
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
import pygame
import requests
import csv
import configparser
import os
import sys
import time
import math
import datetime
import argparse
from io import StringIO
from collections import defaultdict
from shutil import copyfile
import odrive
import signal
import SabertoothPacketSerial
sys.path.insert(0, '/home/pi/r2_control')
from r2utils import telegram, internet, mainconfig

pygame.display.init()

while True:
    pygame.joystick.quit()
    pygame.joystick.init()
    num_joysticks = pygame.joystick.get_count()
    if __debug__:
        print("Waiting for joystick... (count: %s)" % num_joysticks)
    if num_joysticks != 0:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                " : Joystick found \n")
        f.flush()
        break
    time.sleep(5)

pygame.init()
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print("Framebuffer size: %d x %d" % (size[0], size[1]))

j = pygame.joystick.Joystick(0)
j.init()
buttons = j.get_numbuttons()

last_command = time.time()
joystick = True

previous = ""
_throttle = 0
_turning = 0

