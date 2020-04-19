from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

kit.servo[15].angle = 0
time.sleep(1)
kit.servo[15].angle = 90
