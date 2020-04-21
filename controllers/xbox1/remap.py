#!/usr/bin/python
#import requests
import csv
import os
import sys
import time
import datetime
from cStringIO import StringIO
from collections import defaultdict

newkeys = [2,1,4,3,0,5,6,7,8,12,13,9,14,10,11,15,16]

with open ('oldkeys.csv', mode='r') as infile:
	reader = csv.reader(infile)
	for row in reader:
		keys = list(row[0])
		new = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		x = 0
		for k in keys:
			new[newkeys[x]] = k
			x += 1
		print '\"' + ''.join(map(str, new)) + '\",' + row[1] + ',' + row[2]

