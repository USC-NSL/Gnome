import numpy as np
from math import *
import math
import struct
import utm 

TWO_PI = math.pi * 2
PI = math.pi

# plane class used in data exctraction 
class DepthMapPlane:	# size = 16 bytes (4 floats)
	def __init__ (self, blist):
		self.x = b2f(blist[0:4])
		self.y = b2f(blist[4:8])
		self.z = b2f(blist[8:12])
		self.d = b2f(blist[12:16])

	def all(self):
		return [self.x, self.y, self.z, self.d]


# Point3D in x-y-z plane
class Point3D:
	def __init__(self, x_, y_, z_):
		self.x = x_
		self.y = y_
		self.z = z_

	def multiply(self, n):
		self.x *= n
		self.y *= n
		self.z *= n

	def distance(self):
		return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

	def to_array(self):
		return np.array([self.x, self.y, self.z])


# extended point3D with azi and ele 
class Voxel:
	def __init__(self, azi_, ele_, pos_):
		self.azi = azi_ 		# width in the map 
		self.ele = ele_ 		# height (downwards) in the map 
		self.pos = pos_			# a Point3D obj

	def azi_ele(self):
		return [self.azi, self.ele]


# processed plane class 
class Plane:
	def __init__(self, x_, y_, z_, d_):
		self.x = x_
		self.y = y_
		self.z = z_
		self.d = d_

	def all(self):
		return [self.x, self.y, self.z, self.d]


# Point2D in x-y plane
class Point2D():
	def __init__(self, x, y):
		self.x = float(x)
		self.y = float(y)


# calculate the distance (m) between two latlons
# input: [lat, lon], [lat, lon]
def get_distance(origin, destination):
	xy = utm.from_latlon(origin[0], origin[1])
	originXY = Point2D(float(xy[0]), float(xy[1]))
	xy = utm.from_latlon(destination[0], destination[1])
	destinationXY = Point2D(float(xy[0]), float(xy[1]))

	# distance = math.sqrt(destinationXY.y - originXY.y, destinationXY.x - originXY.x) * 180 / math.pi
	distance = math.sqrt((originXY.x - destinationXY.x) ** 2 + (originXY.y - destinationXY.y) ** 2)
	return distance	


# return the relative xy to the origin, return [x,y] (unit in meters)
# input: [lat, lon], [lat, lon]
def relative_xy(origin, destination):
	xy = utm.from_latlon(origin[0], origin[1])
	originXY = Point2D(float(xy[0]), float(xy[1]))

	xy = utm.from_latlon(destination[0], destination[1])
	destinationXY = Point2D(float(xy[0]), float(xy[1]))

	return [(destinationXY.x - originXY.x), (destinationXY.y - originXY.y)]


# input the origin lat,lon and offset x,y, get the new lat,lon
def xy2ll(origin, offset):
	x, y, h, d = utm.from_latlon(float(origin[0]), float(origin[1]))
	x += offset[0]
	y += offset[1]
	return utm.to_latlon(x, y, h, d)


def b2i(data):	# one byte to int
	return struct.unpack('B', data)[0]


def b2f(data):	# 4 bytes to float
	return struct.unpack('f', data)[0]


def precision(f, n=1):	# fix the precision of float 
	p = pow(0.1, n)
	return f - f % p


def ray_intersect(line, azi, origin=[0,0]):
	# point: [x,y]
	# line: [point, point]
	pass		# TODO 


def mirror_point(line, point):
	# point: [x,y]
	# line: [point, point]
	pass		# TODO 


def dist2d(p1, p2):
	return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


###########################
# x: points to east
# y: points to north 
# z: points up
# azi: starting from north, counterclock 
# ele: corner between ground and LOS 
###########################

def to_azi_ele(x, y, z = 0):
	plane_dist = sqrt(x * x + y * y)
	azi = 0
	if plane_dist:
		azi = np.arccos(y / plane_dist)
	if x < 0:
		azi = TWO_PI - azi

	space_dist = sqrt(x * x + y * y + z * z)
	ele = 0
	if space_dist:
		ele = np.arcsin(z / space_dist)
	return azi, ele


def to_unit_xyz(azi, ele=0):
	return 	np.cos(ele) * np.sin(azi), \
			np.cos(ele) * np.cos(azi), \
			np.sin(ele)


# ratio that magnify vector on unit sphere to a plane y = 1
def sphere_plane_ratio(azi, ele):
	return np.tan( np.arcsin( sqrt( np.cos(ele) * np.cos(ele) + \
									np.sin(ele) * np.sin(ele) * \
									np.sin(azi) * np.sin(azi) ) ) )
