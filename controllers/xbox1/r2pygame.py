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
from enum import Enum
sys.path.insert(0, '/home/pi/r2_control')
sys.path.insert(0, '/home/pi/SabertoothPacketSerial/SabertoothPacketSerial')
from SabertoothPacketSerial import SabertoothPacketSerial

from r2utils import mainconfig

def sig_handler(signal, frame):
    """ Handle signals """
    print('Cleaning Up')
    sys.exit(0)

signal.signal(signal.SIGINT, sig_handler)

################################################################################
"""
Generic pygame wrapper class used to initialize a pygame joystick and provides
a run loop to interact with the controller
"""
class R2PygameJoystick:
    def __init__(self):
        """ Constructor """
        self.__joystick = None
        self.__joystick_count = 0
        self.__display_size = []
        self.__hat_count = 0
        return

    __buttonCount = 0
    """Number of buttons associated with the current joystick"""

    debug = False
    """ If true debug messages will be printed """

    joystick_path = '/dev/input/js0'
    """ Joystick path, defaults to '/dev/input/js0 '"""

    def get_display_size(self):
        """Size of the pygame.display"""
        return self.__display_size

    def get_button_count(self):
        """Number of buttons associated with the current joystick"""
        return self.__buttonCount

    def get_hat_count(self):
        """Number of hats (d-pad) associated with the current joystick"""
        return self.__hat_count

    def continue_running(self):
        """
        Override this method and return false when you want the Run loop to exit
        """
        if os.path.exists(self.joystick_path):
            return True
        Trace("Joystick was disconnected")
        return False

    def __initialize(self):
        """Called by Run to connect to and initialize the pygame.joystick"""
        pygame.display.init()

        while True:
            # Check to see if any joysticks are connected
            pygame.joystick.quit()
            pygame.joystick.init()
            self.__joystick_count = pygame.joystick.get_count()
            print("Waiting for joystick... (count: %s)" % self.__joystick_count)
            # Break out of loop when a joystick is found
            if self.__joystick_count != 0:
                break
            # Wait for 5 seconds and try again
            time.sleep(5)
        # Initialize pygame
        pygame.init()
        self.__display_size = (pygame.display.Info().current_w,
                              pygame.display.Info().current_h)
        print("Framebuffer size: %d x %d"
           % (self.__display_size[0], self.__display_size[1]))
        # Get the first joystick
        self.__joystick = pygame.joystick.Joystick(0)
        self.__joystick.init()
        self.__buttonCount = self.__joystick.get_numbuttons()
        self.__hat_count = self.__joystick.get_numhats()
        self.last_command = time.time()

        print("Joystick buttons(%d) hats(%d)" % (self.__buttonCount, self.__hat_count))

        self.on_initialized()
        return

    def run(self):
        """
        Call this method to initialize the connected pygame.joystick and enter a
        message loop that will exit when the controller is disconnected or
        ContinueRunning returns False.
        """
        self.__initialize()
        # if __debug__:
        while (self.continue_running()):
            events = pygame.event.get()
            for event in events:
                self.event_proc(event)
        print("ContinueRunning returned False")
        self.on_exit_run(False)
        # else:
        #     try:
        #         while (self.continue_running()):
        #             events = pygame.event.get()
        #             for event in events:
        #                 self.event_proc(event)
        #         self.on_exit_run(False)
        #     except:
        #         print("Something went wrong!")
        #         self.on_exit_run(True)
        return

    def on_initialized(self):
        """
        Called at the begining of Run after the connected pygame.joystick is
        found and initialized just before entering the Run message loop.
        """
        if __debug__:
            print("pygame Initilized")
        return


    def on_exit_run(self, exceptionCaught):
        """
        Called by Run after continue_running() returns False before the method
        exits.
        """
        if __debug__:
            print("pygame Run loop finished")
        return

    def event_proc(self, event):
        """
        Called by run for each pygame.event encountered, will call the
        apporopriate On... method based on the event.type.
        """
        if __debug__:
            print(event)
        if event.type == pygame.JOYBUTTONDOWN:
            self.on_button_down(event)
        elif event.type == pygame.JOYBUTTONUP:
            self.on_button_up(event)
        elif event.type == pygame.JOYHATMOTION:
            self.on_mat_motion(event)
        elif event.type == pygame.JOYAXISMOTION:
            self.on_axis_motion(event)
        elif event.type == pygame.JOYBALLMOTION:
            self.on_ball_motion(event)
        return

    def get_button_states(self):
        """
        Get an array of current button states, values of 1 indicate a button is
        pressed, 0 if not pressed.
        """
        buttons = [];
        for i in range(self.get_button_count()):
            buttons.append(self.__joystick.get_button(i))
        # Ensure the state array is long enough to map a key string
        while len(buttons) < self.get_key_string_length():
            buttons.append(0)
        return buttons

    def get_hat_states(self, hatIndex):
        """
        Get the current state of all the hats (d-pad buttons).  Will return a
        pair of ints representing the horizontal and vertical button states.
        """
        index = self.__joystick.get_hat(hatIndex)
        return [index[0], index[1]]

    def on_button_down(self, event):
        """Called by EventProc when a joystick button goes down"""
        self.get_button_states()
        return

    def on_button_up(self, event):
        """Called by EventProc when a joystick button goes up"""
        self.get_button_states()
        return

    def on_mat_motion(self, event):
        """Called by EventProc when a pygame.JOYHATMOTION is encountered"""
        self.get_hat_states(0);
        return

    def on_axis_motion(self, ent):
        """Called by EventProc when a pygame.JOYAXISMOTION message is encountered"""
        if __debug__:
            print("OnAxisMotion")
        return

    def on_ball_motion(self, ent):
        """Called by EventProc when a pygame.JOYBALLMOTION message is encountered"""
        if __debug__:
            print("OnBallMotion")
        return

################################################################################
"""Simple class to print controller actions to aid in mapping a controler. """
class R2MapPygameJoystick(R2PygameJoystick):
    def on_button_down(self, event):
        """Overriding to identify button press action"""
        print("OnButtonDown: %s" % event)
        return

    def on_button_up(self, event):
        """Reduce messsage feeback by supressing the button up event"""
        return

    def on_mat_motion(self, event):
        """Overriding to identify hat motion event"""
        print("OnHatMotion: %s" % event)
        return

    def on_axis_motion(self, event):
        """Overriding to identify axis motion event"""
        print("OnAxisMotion: %s" % event)
        return

################################################################################
"""
Generic pygame wrapper around a game controller with two joy sticks, a d-pad,
come buttons on the right, two buttons on the top right and left and a couple
of buttons in the middle.
"""
class R2PygameGamepad(R2PygameJoystick):
    def __init__(self, fileName, description):
        """
        Constructor

        Parameters:
            fileName [in] File name prefix
            description [in] Description passed to log and config files
            debug [in] Set the base class debug flag, this will allow initiliztion
                       messages to print while initializing
        """
        self.__description = description
        self.__key_string_length = 0
        self.__key_state_array = []
        ##########################################################
        # Load config
        self.__configfile = mainconfig.mainconfig['config_dir'] + fileName + '.cfg'
        self.__configfile_defaults = fileName + '.cfg-default'
        self.__keysfile = mainconfig.mainconfig['config_dir'] + fileName + '_keys.csv'
        self.__read_config_file(fileName)

        self.__open_log_file()
        self.__parse_args()
        self.__read_keys_file()
        self.__initialize_drive()

        os.environ["SDL_VIDEODRIVER"] = "dummy"
        ##########################################################
        # Set variables
        ##########################################################
        # How often should the script send a keepalive (s)
        self.keep_alive = float(self.__mainConfig['keepalive'])

        # Speed factor. This multiplier will define the max value to be sent to the drive system.
        # eg. 0.5 means that the value of the joystick position will be halved
        # Should never be greater than 1
        self.speed_fac = float(self.__mainConfig['speed_fac'])

        # Invert. Does the drive need to be inverted. 1 = no, -1 = yes
        self.invert = int(self.__mainConfig['invert'])

        self.drive_mod = self.speed_fac * self.invert

        # Set Axis definitions
        self.axis_left_vertical = int(self.__config.get('Axis', 'drive'))
        self.axis_left_horizontal = int(self.__config.get('Axis', 'turn'))
        self.axis_right_horizontal = int(self.__config.get('Axis', 'dome'))
        if __debug__:
            print("left horizontal:" +str(self.axis_left_horizontal) + "  left vertical:" + str(self.axis_left_vertical) + "  right horizontal:" + str(self.axis_right_horizontal))
        # Base URL used to send get requests
        self.base_url = self.__mainConfig['baseurl']
        # Current key associated with the last button down event
        self.key_string = ""
        # Last button down event key string, will play the up action assoicated
        # with this key on button up
        self.previous_key_string = ""
        # Drive variables
        self.turning = 0
        self.throttle = 0
        # Play starup sound
        self.requests_get("audio/Happy007", "Getting read to load " + self.__description + " controller")
        return

    def __read_keys_file(self):
        """ Parse keys file and populte the self.__keys dictionary """
        # Check theres a keys config file:
        if not os.path.isfile(self.__keysfile):
            copyfile('keys-default.csv', _keysfile)

        # Read in key combos from csv file
        self.__keys = defaultdict(list)
        with open(self.__keysfile, mode='r') as infile:
            reader = csv.reader(infile)
            for row in reader:
                if __debug__:
                    print("Row: %s | %s | %s" % (row[0], row[1], row[2]))
                self.__keys[row[0]].append(row[1])
                self.__keys[row[0]].append(row[2])
                # Set the __key_string_length based on the first key in the dictionary
                # this is used by get_key_string to size the key string
                self.__key_string_length = max(self.__key_string_length, len(row[0]))
        # Print the keys dictionary
        list(self.__keys.items())
        return

    def __parse_args(self):
        parser = argparse.ArgumentParser(description=self.__description + ' controller for r2_control.')
        parser.add_argument('--curses', '-c', action="store_true", dest="curses", required=False,
                            default=False, help='Output in a nice readable format')
        parser.add_argument('--dryrun', '-d', action="store_true", dest="dryrun", required=False,
                            default=False, help='Output in a nice readable format')
        self.__args = parser.parse_args()

        self.dryrun = self.__args.dryrun
        self.dryrun = True;

        if self.__args.curses:
            print('\033c')
            self.locate("-=[ " + self.__description + " Controller ]=-", 10, 0)
            self.locate("Left", 3, 2)
            self.locate("Right", 30, 2)
            self.locate("Joystick Input", 18, 3)
            self.locate("Drive Value (    )", 16, 7)
            self.locate('%4s' % speed_fac, 29, 7)
            self.locate("Motor 1: ", 3, 11)
            self.locate("Motor 2: ", 3, 12)
            self.locate("Last button", 3, 13)
        return

    def __initialize_drive(self):
        if not self.dryrun:
            if __debug__:
                print("Not a drytest")
            if self.__config.get('Drive', 'type') == "Sabertooth":
                self.drive = SabertoothPacketSerial(address=int(self.__config.get('Drive', 'address')),
                                                    type=self.__config.get('Drive', 'type'),
                                                    port=self.__config.get('Drive', 'port'))
				# self.dome = SabertoothPacketSerial(address=int(_config.get('Dome', 'address')),
				#                                     type=_config.get('Dome', 'type'),
				#                                     port=_config.get('Dome', 'port'))
            elif self.__config.get('Drive', 'type') == "ODrive":
                print("finding an odrive...")
                self.drive = odrive.find_any()
                self.drive.axis1.controller.vel_ramp_enable = True
                self.drive.axis0.controller.vel_ramp_enable = True
        return

    def __open_log_file(self):
        log_file = self.__mainConfig['log_file']
        #### Open a log file
        self.__logFile = open(log_file, 'at')
        self.log_message(" : ****** " + self.__description + " started ******")
        return

    def __read_config_file(self, fileName):
        self.__config = configparser.SafeConfigParser({'log_file': '/home/pi/r2_control/logs/' + fileName + '.log',
                                                 'baseurl' : 'http://localhost:5000/',
                                                 'keepalive' : 0.25,
                                                 'speed_fac' : 0.35,
                                                 'invert' : -1,
                                                 'accel_rate' : 0.025,
                                                 'curve' : 0.6,
                                                 'deadband' : 0.2})
        # Add default values to configuration dictionary
        self.__config.add_section('Dome')
        self.__config.set('Dome', 'address', '129')
        self.__config.set('Dome', 'type', 'Syren')
        self.__config.set('Dome', 'port', '/dev/ttyUSB0')
        self.__config.add_section('Drive')
        self.__config.set('Drive', 'address', '128')
        self.__config.set('Drive', 'type', 'Sabertooth')
        self.__config.set('Drive', 'port', '/dev/ttyACM0')
        self.__config.add_section('Axis')
        self.__config.set('Axis', 'drive', '1')
        self.__config.set('Axis', 'turn', '0')
        self.__config.set('Axis', 'dome', '3')

        # Load values from default dictionary if provided
        if os.path.isfile(self.__configfile_defaults):
            print("Getting defaults from: " + self.__configfile_defaults)
            self.__config.read(self.__configfile_defaults)

        # Write the runtime configuration file if it is not found
        if not os.path.isfile(self.__configfile):
            print("Config file does not exist")
            with open(self.__configfile, 'wb') as configfile:
                self.__config.write(configfile)

        # Read the final configuration file
        self.__mainConfig = self.__config.defaults()
        return

    def get_key_string_length(self):
        return self.__key_string_length;

    def continue_running(self):
        """
        Override this method and return false when you want the Run loop to exit
        """
        # Add game controller steering code and to check for the presence of a
        # shutdown file
        if not R2PygameJoystick.continue_running(self):
            return False
        self.steering(self.turning, self.throttle)
        difference = float(time.time() - self.last_command)
        if difference > self.keep_alive:
            # if __debug__:
            #     print("Last command sent greater than %s ago, doing keepAlive" % self.keep_alive)
            # Check for no shutdown file
            if os.path.exists('/home/pi/r2_control/controllers/.shutdown'):
                print("Shutdown file is there")
                return False
            else:
	            self.last_command = time.time()
        return True

    def on_exit_run(self, exceptionCaught):
        """
        Called by Run after continue_running() returns False before the method exits.
        """
        if exceptionCaught:
            print("OnExitRun exceptionCaught is True")
            self.shutdown_r2()
        return

    def locate(self, userString, x, y):
        """ Place the text at a certain location """
        # Don't allow any user errors. Python's own error detection will check for
        # syntax and concatination, etc, etc, errors.
        x = max(0, min(int(x), 80))
        y = max(0, min(int(y), 40))
        # Plot the user_string at the starting at position HORIZ, VERT...
        print("\033["+self.str(y)+";"+str(x)+"f"+userString)
        return

    # Gets the button down array and converts it to a button key string using the
    # KeyIndexFromButton method to map the button index to the key string.
    def get_key_string(self):
        # Make sure state array is big enough to hold the button states and the
        # key string
        l = max(self.get_button_count(), self.__key_string_length)
        while len(self.__key_state_array) < l:
            self.__key_state_array.append(0)
        # Get the button state array, may be larger than the button count if the
        # controller has expanded it to hold additional key string data
        states = self.get_button_states()
        # Map the button state index to the key string
        for i in range(len(states)):
            self.__key_state_array[self.key_index_from_button(i)] = states[i]
        # Return the key state array as a string
        return ''.join(map(str, self.__key_state_array))


    def key_index_from_button(self, buttonIndex):
        """
        Returns a button index converted to a keystring index, by default it simply
        returns buttonIndex.  Use this to map a controller button directly to a key
        digit.
        """
        return buttonIndex

    def log_message(self, logString):
        """
        Write message to log file, includes exception handling should writing fail
        """
        try:
            self.__logFile.write(datetime.datetime.fromtimestamp(time.time()).strftime(
                                 '%Y-%m-%d %H:%M:%S') + logString + " \n")
            self.__logFile.flush()
        except:
            if __debug__:
                print ("Error writing log file")
        return

    def requests_get(self, url, logString):
        """
        Log event then attempt to make get request using the specified URL
        """
        try:
            self.log_message(logString)
            return requests.get(self.base_url + url)
        except:
            if __debug__:
                print("Get request failed....")
            return ""

    def locate_if_curses(self, key, x, y):
        """
        Will call self.Locate if args.curses only is True.
        """
        if self.__args.curses:
            self.locate(key, x, y)
        return

    def speed_up_or_slow_down_drive(self, speedUp):
        """
        Will increment or decrement the SpeedFac by 0.5 and give some audio
        feedback.
        """
        if __debug__:
            print("Incrementing drive speed" if speedUp else "Decrementing drive speed")
        # Calculate the new SppedFac clamping at 0.2 and 1.0
        self.speed_fac = min(1.0, self.speed_fac + 0.05) if sppedUp else max(0.2, self.speed_fac - 0.05)
        if __debug__:
            print("*** NEW SPEED %s" % self.speed_fac)
        self.locate_if_curses('%4f' % self.speed_fac, 28, 7)
        self.drive_mod = self.speed_fac * self.invert
        logstr = " : Speed Increase : " if speedUp else " : Speed Decrease : " + str(self.speed_fac)
        self.requests_get("audio/Happy006" if speedUp else "audio/Sad__019", logstr)
        return

    SpeedUpDriveKey = "00001111000000001"
    SlowDownDriveKey = "00001111000000010"

    def button_pressed(self):
        """ Call this method when a controller button goes down

        Method will get a key string based on the currently pressed buttons,
        store it in self.key_string.  Looks in the keys dictionary for actions
        mapped to the currently down buttons and sends get request.  Special
        cases speed up and slow down button combinations.
        """
        # Build the new key string based on the currently pressed buttons
        self.key_string = self.get_key_string()
        if __debug__:
            print("Buttons pressed(%s)" % self.key_string)
        self.locate_if_curses("                   ", 1, 14)
        self.locate_if_curses(self.key_string, 3, 14)
        # Special key press (All 4 plus triangle) to increase speed of drive
        if self.key_string == self.SpeedUpDriveKey:
            self.speed_up_or_slow_down_drive(True)
        # Special key press (All 4 plus X) to decrease speed of drive
        elif self.key_string == self.SlowDownDriveKey:
            self.speed_up_or_slow_down_drive(False)
        try:
            # Find the actions associated with the new key string and make a get
            # request
            key = self.__keys[self.key_string]
            url = key[0]
            logstr = " : Button Down event : " + self.key_string + "," + url;
            if __debug__:
                print("Would run: %s" % key)
                print("URL: %s" % self.base_url + url)
            self.requests_get(url, logstr)
            self.previous_key_string = self.key_string
        except:
            if self.debug:
                print("No connection")
        return

    def button_released(self):
        """
        Call this when a button comes back up.  Will used the cached button down
        key string to look up the button up url and get it.
        """
        if self.debug:
            print("Buttons released: %s" % self.previous_key_string)
        try:
            # Get key up action
            key = self.__keys[self.previous_key_string]
            url = key[1]
            logstr = " : Button Up event : " + self.previous_key_string + "," + key[1];
            # Log key up action
            if __debug__:
                print("Would run: %s" % key[1])
                print("URL: %s" % url)
            self.requests_get(url, logstr)
        except:
            if __debug__:
                print("No combo (released)")
        self.previous = ""
        return

    def axis_motion(self, axis, value):
        """
        Call when one of the joysticks move to handle the joystick move event
        """
        if axis == self.axis_left_vertical:
            if __debug__:
                print("Value (Drive): %s : Speed Factor : %s" % (value, self.speed_fac))
            self.locate_if_curses("                   ", 10, 4)
            self.locate_if_curses('%10f' % (value), 10, 4)
            self.throttle = value
            self.last_command = time.time()
        elif axis == self.axis_left_horizontal:
            if __debug__:
                print("Value (Steer): %s" % value)
            self.locate_if_curses("                   ", 10, 5)
            self.locate_if_curses('%10f' % (value), 10, 5)
            self.turning = value
        elif axis == self.axis_right_horizontal:
            if __debug__:
                print("Value (Dome): %s" % value)
            self.locate_if_curses("                   ", 35, 4)
            self.locate_if_curses('%10f' % (value), 35, 4)
            self.log_message(" : Dome : " + str(value) + "\n")
            if not self.dryrun and __debug__:
                print("Not a drytest")
            self.locate_if_curses("                   ", 35, 8)
            self.locate_if_curses('%10f' % (value), 35, 8)
            self.last_command = time.time()
        return

    def steering(self, x, y):
        """ Steer the droid

        Combine Axis output to power differential drive motors
        """
        # convert to polar
        r = math.hypot(x, y)
        t = math.atan2(y, x)

        # rotate by 45 degrees
        t += math.pi / 4

        # back to cartesian
        left = r * math.cos(t)
        right = r * math.sin(t)

        # rescale the new coords
        left = left * math.sqrt(2)
        right = right * math.sqrt(2)

        # clamp to -1/+1
        left = (max(-1, min(left, 1)))*self.drive_mod
        right = (max(-1, min(right, 1)))*self.drive_mod

        if not self.dryrun:
            if self.__config.get('Drive', 'type') == "Sabertooth":
                self.drive.motor(0,left)
                self.drive.motor(1,right)
            elif self.__config.get('Drive', 'type') == "ODrive":
                self.drive.axis0.controller.vel_ramp_target = left*1000
                self.drive.axis1.controller.vel_ramp_target = right*1000

        self.locate_if_curses('%10f' % left, 13, 11)
        self.locate_if_curses('%10f' % right, 13, 12)

        return left, right

    def shutdown_r2(self):
        """ Put R2 into a safe state """
        print("Running shutdown procedure")
        if __debug__:
            print("Stopping all motion...")
            print("...Setting drive to 0")
        self.steering(0, 0)
        if __debug__:
            print("...Setting dome to 0")

        self.Dome.driveCommand(0)

        if __debug__:
            print("Disable drives")
        self.requests_get("servo/body/ENABLE_DRIVE/0/0", "Disable drives on shutdown")

        if __debug__:
            print("Disable dome")
        self.requests_get("servo/body/ENABLE_DOME/0/0", "Disable dome on shutdown")

        # Play a sound to alert about a problem
        self.requests_get("audio/MOTIVATR", " ****** " + self.__description + " Shutdown ******")
        return
