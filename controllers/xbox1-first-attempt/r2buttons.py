import csv
#import pygame

#-----------------------------------------------------------------------------------------
# Key (button string) length
BUTTON_STRING_LENGTH = 17

#-----------------------------------------------------------------------------------------
#
# Description:
#   Remap from controller to system button index
#-----------------------------------------------------------------------------------------
to_controller_remap = []
#-----------------------------------------------------------------------------------------
#
# Description:
#   Remap from system button controller index
#-----------------------------------------------------------------------------------------
to_system_remap = []

#-----------------------------------------------------------------------------------------
# 
# Description:
#   Make sure button index (Id) is greater than 0 and less than BUTTON_STRING_LENGTH
# Returns:
#   Returns true if the i is greater than 0 and less than BUTTON_STRING_LENGTH indicating
#   it is a valid sub string index.
#-----------------------------------------------------------------------------------------
def buttonIndexIsValid(i):
	return i > -1 and i < BUTTON_STRING_LENGTH

#-----------------------------------------------------------------------------------------
#
# Description:
#   Open the button_map.csv file and populate the remap arrays
#-----------------------------------------------------------------------------------------
def loadButtonMaps():
	# Resize the remap arrays to the key length
	while len(to_controller_remap) < BUTTON_STRING_LENGTH:
		to_controller_remap.append(0)
	while len(to_system_remap) < BUTTON_STRING_LENGTH:
		to_system_remap.append(0)
	# Get the system button index to controller values
	with open ('button_map.csv', mode='r') as infile:
		reader = csv.reader(infile)
		for row in reader:
			# Make sure there are two columns in the row, columns after the second can
			# bu used for notes
			if len(row) > 1 and len(row[0]) > 0 and row[0][0] != '#':
				# Convert both tokens to ints
				x = int(row[0])
				y = int(row[1])
				# Make sure the values are in range
				if buttonIndexIsValid(x) and buttonIndexIsValid(y):
					# Map the controller button index to the system index
					to_controller_remap[x] = y
					to_system_remap[y] = x

#-----------------------------------------------------------------------------------------
#
# Description:
#   If toSystem is true it return the controller to system array otherwise return the
#   system to controller array.
# Parameters:
#	toSystem [in] If true returns the controller to system array otherwise; returns the
#   system to controller array. 
# Returns:
#   Demand load the remap arrays and return the appropriate array when done.
#-----------------------------------------------------------------------------------------
def buttonMap(toSystem):
	# Load the remap arrays if either of them is uninitialized
	if len(to_system_remap) < BUTTON_STRING_LENGTH or len(to_controller_remap) < BUTTON_STRING_LENGTH:
		loadButtonMaps()
	# Return the appropriate array
	if toSystem:
		return to_system_remap
	return to_controller_remap

#-----------------------------------------------------------------------------------------
#
# Description:
#   Make sure string is >= BUTTON_STRING_LENGTH by appending '0' to the end until it is
#   long enough
# Parameters:
#   s [in] Button state string
# Returns:
#   Returns a button state string BUTTON_STRING_LENGTH or longer, pads s with '0' if it
#   is short.
#-----------------------------------------------------------------------------------------
def padKeyString(s):
	# Make sure string is >= BUTTON_STRING_LENGTH by appending '0' to the end until it
	# is long enough
	while len(s) < BUTTON_STRING_LENGTH:
		s = s + "0"
	return s;

#-----------------------------------------------------------------------------------------
#
# Description:
#   Convert a button string (list of which buttons are down)
#   If toSystem is true it converts the string from a controller to system string
#   otherwise; converts from system to controller string.
# Parameters:
#   s [in] Button state string
#   toSystem [in] 
#     If true converts from controller to system list otherwise converts from system to
#     controller list.
# Returns:
#   Returns the remapped button state string
#-----------------------------------------------------------------------------------------
def getKeyString(s, toSystem):
	# Make sure string is >= BUTTON_STRING_LENGTH by appending '0' to the end until it
	# is long enough
	s = padKeyString(s)
	# Output for remapped values
	remapped = []
	for i in range(BUTTON_STRING_LENGTH):
		remapped.append(0)
	# Get the appropriate remap index array
	remap = buttonMap(toSystem)
	# Resort the button character array int the remapped list
	i = 0
	for c in s:
		remapped[remap[i]] = c
		i += 1
	# Convert the remapped array to a string
	return ''.join(map(str, remapped))

#-----------------------------------------------------------------------------------------
#
# Description:
#   Get current button states
# Parameters:
#   joyStick [in]
#   buttonCount [in]
#   s [in] Button state string
#   toSystem [in]
#     If true converts from controller to system list otherwise converts from system to
#     controller list.
# Returns:
#   Returns a string containing '1' for keys that are down and '0' when the key is up.
#   Will pad the string to ensure it is BUTTON_STRING_LENGTH or longer
#-----------------------------------------------------------------------------------------
def getButtonStateString(joyStick, buttonCount, toSystem):
	buf = StringIO()
	for i in range(buttonCount):
		button = joyStick.get_button(i)
		buf.write(str(button))
	result = paddKeyString(buf.getvalue())
	if toSystem:
		return getKeyString(result)
	return result

#-----------------------------------------------------------------------------------------
#
# Description:
#
#   Test code, convert to system string then back to make sure it works
#
#-----------------------------------------------------------------------------------------
'''
xboxkey = "12345678912345678"
print(xboxkey)
systemkey = getKeyString(xboxkey, True)
print(systemkey)
newxboxkey = getKeyString(systemkey, False)
print(newxboxkey)
'''
