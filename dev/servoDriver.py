import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

print ('Set servo angles to 0')

for i in range(4):
	kit.servo[i].angle = 0
	time.sleep(1)

print ('Set servo angles to 90')

for i in range(4):
	kit.servo[i].angle = 90
	time.sleep(1)

print ('Done...')
