#import evdev
from evdev import InputDevice, categorize, ecodes

#creates object 'gamepad' to store the data
#you can call it whatever you like
gamepad = InputDevice('/dev/input/event1')

#prints out device info at start
print(gamepad)

btnRight = 311
btnLeft  = 310
btnA     = 304
btnB     = 305
btnX     = 307
btnY     = 308
btnMenu  = 308
btnBack  = 307

def printButtonEvent(event):
    if event.code == btnA:
        print("A : " + str(event.code))
    elif event.code == btnB:
        print("B : " + str(event.code))
    elif event.code == btnX:
        print("X : " + str(event.code))
    elif event.code == btnY:
        print("Y : " + str(event.code))
    elif event.code == btnLeft:
        print("Left : " + str(event.code))
    elif event.code == btnRight:
        print("Right : " + str(event.code))
    elif event.code == btnMenu:
        print("Menu : " + str(event.code))
    elif event.code == btnBack:
        print("Back : " + str(event.code))
    else:
        print("Unknown button: " + str(event.code))

    
#evdev takes care of polling the controller in a loop
#loop and filter by event code and print the mapped label
for event in gamepad.read_loop():
    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            printButtonEvent(event)
