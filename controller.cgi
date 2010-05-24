#!/usr/bin/python
import cgitb; 
#cgitb.enable()
import cgi
import sys
import json
from rmesh import *
from os import environ
	
points = []

data = cgi.FieldStorage()
points = data.getlist("points")
pointList = []

for p in points:
	# Normalize point from (x,y) to [x,y]
	p2 = p.split(",")
	# Create new Point_2 and append
	point = Point_2(float(p2[0]), float(p2[1]))
	pointList.append(point)

# Create our new rmesh bohemoth
rm = RM_Rmesh(pointList)

# Compute it all! (This may take a while)
rm.compute()

# Build and serve json
data = rm.buildJson()
print 'Pragma: no-cache'
print "Content-type: text/html;charset=utf-8\r\n"
print json.dumps(data)
