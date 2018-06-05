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
	x, y, _ = to_unit_xyz(float(azi) * PI / 180.)

	ray = [origin, [origin[0] + x, origin[1] + y]]
	xi, yi, has_int, _, _ = intersectLines(line[0], line[1], ray[0], ray[1])
	if not has_int:
		return []

	if xi > min(line[0][0], line[1][0]) and xi < max(line[0][0], line[1][0]) \
		and yi > min(line[0][1], line[1][1]) and yi < max(line[0][1], line[1][1]) \
		and ((x == 0 or (xi - origin[0])/x > 0) and (y == 0 or (yi - origin[1])/y > 0)):
		return [xi, yi]

	return []	


def line_para(line):
	# [p1, p2] -> y = ax + c
	p1, p2 = line
	if p1[0] == p2[0]:
		return None, None
	a = float(p2[1] - p1[1]) / float(p2[0] - p1[0])
	c = float(p1[1]) - a * p1[0]
	return a, c


def mirror_point(line, point):
	# point: [x,y]
	# line: [point, point]
	x, y = map(float, point)
	if line[0][0] == line[1][0]:	# vertical line 
		return [2 * line[0][0] - x, y]
	a, c = line_para(line)
	d = (x + (y - c) * a) / (1 + a * a)
	return [2 * d - x, 2 * d * a - y + 2 * c]


def dist2d(p1, p2):
	return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def intersectLines( pt1, pt2, ptA, ptB ): 
    """ this returns the intersection of Line(pt1,pt2) and Line(ptA,ptB)
        
        returns a tuple: (xi, yi, valid, r, s), where
        (xi, yi) is the intersection
        r is the scalar multiple such that (xi,yi) = pt1 + r*(pt2-pt1)
        s is the scalar multiple such that (xi,yi) = pt1 + s*(ptB-ptA)
            valid == 0 if there are 0 or inf. intersections (invalid)
            valid == 1 if it has a unique intersection ON the segment    """

    DET_TOLERANCE = 0.000001

    # the first line is pt1 + r*(pt2-pt1)
    # in component form:
    x1, y1 = pt1;   x2, y2 = pt2
    dx1 = x2 - x1;  dy1 = y2 - y1

    # the second line is ptA + s*(ptB-ptA)
    x, y = ptA;   xB, yB = ptB;
    dx = xB - x;  dy = yB - y;

    # we need to find the (typically unique) values of r and s
    # that will satisfy
    #
    # (x1, y1) + r(dx1, dy1) = (x, y) + s(dx, dy)
    #
    # which is the same as
    #
    #    [ dx1  -dx ][ r ] = [ x-x1 ]
    #    [ dy1  -dy ][ s ] = [ y-y1 ]
    #
    # whose solution is
    #
    #    [ r ] = _1_  [  -dy   dx ] [ x-x1 ]
    #    [ s ] = DET  [ -dy1  dx1 ] [ y-y1 ]
    #
    # where DET = (-dx1 * dy + dy1 * dx)
    #
    # if DET is too small, they're parallel
    #
    DET = (-dx1 * dy + dy1 * dx)

    if math.fabs(DET) < DET_TOLERANCE: return (0,0,0,0,0)

    # now, the determinant should be OK
    DETinv = 1.0/DET

    # find the scalar amount along the "self" segment
    r = DETinv * (-dy  * (x-x1) +  dx * (y-y1))

    # find the scalar amount along the input line
    s = DETinv * (-dy1 * (x-x1) + dx1 * (y-y1))

    # return the average of the two descriptions
    xi = (x1 + r*dx1 + x + s*dx)/2.0
    yi = (y1 + r*dy1 + y + s*dy)/2.0
    return ( xi, yi, 1, r, s )


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
