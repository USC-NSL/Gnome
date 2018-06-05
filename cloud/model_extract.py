# sv_depth.py by xc
# function: read in GPS locations, get surrounding depth info
# output: 	
# 		voxels: {planeId: Voxel}
# 		planes: {planeId: Plane}
# 		hulls: {planeId: [[Voxel, Voxel], [V, V], ...]}
# 		direction: in degree (street direction)

'''
NOTE:
- Input: 
	lat,lng must be ground turth locations where SV is taken
- Coordinate: 
	azimuth=0: positive y-axis, ranges 0 ~ 180
	elevation=0: positive z-axis, ranges 0 ~ 360
	xyz cooridinates: right hand 
'''

import sys
import os 
import urllib
import numpy 
import base64 
import zlib
import struct
from math import *
import numpy as np
import sys 
import scipy
from scipy.spatial import ConvexHull

import model_plot 
from geometry import *
from support import ll_to_str


MODES = ['planes','points','hulls']	# Select what to be display by model_plot 
IMG_MODE = MODES[0]

URL = 'http://cbk0.google.com/cbk?output=xml&ll=%s&dm=1'

MIN_SURFACE_SIZE = 80
WIDTH = 512
HEIGHT = 256
VERTICAL_THRES = 0.7

DEBUG = False 


def download(ll, data_dir):				# download depth info from google 
	ll_str = ll_to_str(ll)
	raw_file = data_dir + ll_str + '_b64.txt'
	if os.path.exists(raw_file):						# load data from file
		print('fetching depth from txt: ' + raw_file)
		data = open(raw_file).read().splitlines()
		return float(data[0])
	else:					
		print('fetching depth from URL: ' + URL%(ll_str))	# download data & save
		data = urllib.urlopen(URL%(ll_str)).read()
		direction = data.split('pano_yaw_deg=\"')[-1].split('\" tilt_yaw_deg=')[0]
		depth_raw = data.split('</depth_map>')[0].split('<depth_map>')[-1]
		fout = open(raw_file, 'w')
		fout.write(direction + '\n')
		fout.write(depth_raw)
		fout.close()
		return float(direction)


def add_dict(k,v,d):
	if k in d:
		d[k].append(v)
	else:
		d[k] = [v]

												# pack the extract data into our objs
def to_pts(mapWidth, mapHeight, depthmapIndices, depthmapPlanes, rotation=0):
	voxels = {}
	planes = {}
	max_height = 0
	min_dist = 1
	for wid in range(mapWidth):
		for hei in range(mapHeight):
			planeId = depthmapIndices[hei * mapWidth + wid]
			if planeId <= 0:
				continue

			rad_azimuth = float(wid) / float(mapWidth - 1) * TWO_PI
			rad_azimuth += float(360 - rotation) / TWO_PI
			rad_azimuth %= TWO_PI
			rad_elevation = float(mapHeight / 2 - hei) / float(mapHeight - 1) * PI
			pos_x, pos_y, pos_z = to_unit_xyz(rad_azimuth, rad_elevation)

			pos = Point3D(pos_x, pos_y, pos_z)

			plane = depthmapPlanes[planeId]
			if abs(plane.z) > VERTICAL_THRES:		# ignore ground planes
				continue 

			dist = plane.d / (pos.x*plane.x + pos.y*plane.y + pos.z*plane.z) 
			if dist < min_dist:
				min_dist = dist

			pos.multiply(dist)
			if pos.z > max_height:
				max_height = pos.z
													# add rotation to voxels 
			add_dict(planeId, Voxel(int((wid + rotation * WIDTH / 360.) % WIDTH), hei, pos), voxels)
			planes[planeId] = plane

	print('max height %d' % max_height)
	print('min dist %d' % min_dist)
	return voxels, planes


def process_depth(data, rotation):					# process raw data 
	print('parsing data')
	
	data += '=' * ((4 - len(data) % 4) % 4)
	# print('data length %d' % len(data))
	try:
		depth_map = base64.urlsafe_b64decode(data)
	except TypeError:
		print('ERROR: cannot decode b64 (padding)')
		return 
	try: 
		depth_map = zlib.decompress(depth_map)
	except:
		print('ERROR: cannot decompress!')
		return 

	header = ' '.join(x.encode('hex') for x in depth_map[:8])
	# print('Data size: %s header: %s' % (`len(depth_map)`, header))

	headersize = b2i(depth_map[0])
	numPanos = b2i(depth_map[1]) | (b2i(depth_map[2]) << 8)
	mapWidth = b2i(depth_map[3]) | (b2i(depth_map[4]) << 8)
	mapHeight = b2i(depth_map[5]) | (b2i(depth_map[6]) << 8)
	panoIndicesOffset = b2i(depth_map[7])
	# print('numPanos: %d width: %d height: %d panoOffset: %d' % \
	#		(numPanos, mapWidth, mapHeight, panoIndicesOffset))
	if headersize != 8 or panoIndicesOffset != 8: 
		print("ERROR: Unexpected depth map header")
		return

	global WIDTH
	global HEIGHT
	if WIDTH != mapWidth or HEIGHT != mapHeight:
		print('WARNING: different image size! %dx%d' % (mapWidth, mapHeight))
		WIDTH = mapWidth
		HEIGHT = mapHeight

	depthmapIndices = []	# registration of all panorama pixel 
	for i in range(panoIndicesOffset, panoIndicesOffset + mapWidth * mapHeight):
		depthmapIndices.append(b2i(depth_map[i]))

	depthmapPlanes = []		# dict of planes 
	for i in range(panoIndicesOffset + mapWidth * mapHeight, len(depth_map), 16):
		depthmapPlanes.append(DepthMapPlane(depth_map[i : i + 16]))

	# for p in depthmapPlanes:
	# 	print p.all()

	return to_pts(mapWidth, mapHeight, depthmapIndices, depthmapPlanes, rotation)
	

def convex_hull(voxels):			# find convex hull of planes 
	hulls = {}		
	used_surface = 0
	for plane in voxels:
		if len(voxels[plane]) < MIN_SURFACE_SIZE:  # ignore surface with too few points
			continue
		used_surface += 1
		pts = []
		hulls[plane] = []
		for v in voxels[plane]:
			pts.append(v.azi_ele())

		hull = None
		try:
			hull = ConvexHull(pts)			
		except scipy.spatial.qhull.QhullError:
			print('skip the plane for hull extraction')
			continue

		for simplex in hull.simplices:
			first = voxels[plane][simplex[0]]
			second = voxels[plane][simplex[1]]
			hulls[plane].append([first, second])	# format: [pt1, pt2]
		# print('plane #%d - boundary #%d' % (plane, len(res[plane])))
	print('convex hull done: %d surfaces' % (used_surface))
	return hulls


def write_pts(fname, voxels):						# save downloaded data into file
	fout = open(fname, 'w')
	fout.write(`HEIGHT * WIDTH` + '\n')
	for p in voxels:
		for v in voxels[p]:
			fout.write(`v.pos.x` + '\t' + `v.pos.y` + '\t' + `v.pos.z` + '\n')	# write file 
	fout.close() 


def raise_height(hull, height):		# for adjusting convext hull
	for line in hull:
		if line[0].ele < 100.:
			line[0].ele -= height
		if line[1].ele < 100.:
			line[1].ele -= height


def summarize_plane(voxels):
	min_azi, max_azi = 999., -999.
	min_point, max_point = None, None
	max_height = -1

	visited_azi = []
	for v in voxels:
		if v.azi < min_azi:
			min_point = v
			min_azi = v.azi
		if v.azi > max_azi:
			max_point = v
			max_azi = v.azi
		if v.pos.z > max_height:
			max_height = v.pos.z
		if not v.azi in visited_azi:
			visited_azi.append(v.azi)

	if min_azi == 0 and max_azi == WIDTH - 1:
		# print('Cross-image plane..')
		min_point, max_point = None, None
		
		visited_azi.sort()
		boundary_left = 0
		boundary_right = 0
		for i in range(len(visited_azi) - 1):
			if visited_azi[i + 1] - visited_azi[i] > 10:
				boundary_left = visited_azi[i]
				boundary_right = visited_azi[i + 1]
				break 

		for v in voxels:
			if v.azi == boundary_left:
				max_point = v
			if v.azi == boundary_right:
				min_point = v
			if min_point and max_point:
				break 

	edges = [[min_point.pos.x, min_point.pos.y],
			[max_point.pos.x, max_point.pos.y]]

	return edges, max_height + 2


def read_model(fpath):
	rotation, model_raw = open(fpath, 'r').read().splitlines()
	voxels, _ = process_depth(model_raw, float(rotation))
	model_plot.plot_map(fpath + '_v.png', voxels)
	model_plot.save_image(fpath + '.png', voxels, 'planes') 

	res = {}
	for pid in voxels:
		if len(voxels[pid]) < MIN_SURFACE_SIZE:
			continue
		edges, height = summarize_plane(voxels[pid])
		res[pid] = {'edges': edges, 'height': height}
	# print(res)
	return res 


if DEBUG:
	depth_ll = [34.0482559,-118.2574249]
	dst_dir = 'res/'

	voxels, planes, hulls = run(depth_ll, dst_dir, rotation=38.89)	# extract depth info and planes 
	imgname = dst_dir + `depth_ll[0]` + '_' + `depth_ll[1]` + '.bmp' 	# create the image 
	print(imgname)
	model_plot.save_image(imgname, voxels, 'planes') 
	model_plot.load_img(imgname)

	for plane in hulls:													# show the planes
		# raise_height(hulls[plane], 12.)
		print('plane %d' % plane)
		# model_plot.load_img(imgname)
		model_plot.add_hull(imgname, hulls[plane])
	model_plot.show_img()