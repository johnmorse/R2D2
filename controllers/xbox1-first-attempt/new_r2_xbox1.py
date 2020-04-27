import os
import sys
sys.path.insert(0, '/home/pi/r2pylib/controler')
from r2pygame import R2PygameGamepad

BUTTON_COUNT = 17

class XBox1Controller(R2PygameGamepad):
    def get_button_states(self):
        states = R2PygameGamepad.get_button_states(self);
        while len(states) < BUTTON_COUNT:
            states.append(0)
        hats = self.get_hat_states(0)
        states[8] = 1 if hats[1] > 0 else 0
        states[9] = 1 if hats[1] < 0 else 0
        states[15] = 1 if hats[0] < 0 else 0
        states[16] = 1 if hats[0] > 0 else 0
        return states

    def on_mat_motion(self, event):
        print("OnHatMotion")
        hats = self.get_hat_states(0)
        if hats[0] == 0 and hats[1] == 0:
            self.button_released()
        else:
            self.button_pressed()

    def on_button_down(self, event):
        self.button_pressed()

    def on_button_up(self, event):
        self.button_released()

    def on_axis_motion(self, event):
        self.axis_motion(event.axis, event.value)

    """
    Map XBox-One buttons to PS-3 equivelent
    """
    def key_index_from_button(self, buttonIndex):
        switcher={
            0:0,   # Cross
            1:1,   # Circle
            4:2,   # Triangle
            3:3,   # Square
            2:4,   # L2
            5:5,   # R2
            6:6,   # L1
            7:7,   # R1
            10:8,  # Select
            11:9,  # Start
            12:10, # Menu
            13:11, # L3
            14:12, # R3
            8:13,  # Up
            9:14,  # Down
            15:15, # Left
            16:16  # Right
            }
        return switcher.get(buttonIndex,buttonIndex)

_controller = XBox1Controller(BUTTON_COUNT, "xbox1", "XBOX1", True)
_controller.run()
