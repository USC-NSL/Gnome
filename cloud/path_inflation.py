import sys 
import pickle
import numpy as np
import support
import geometry 
import model_extract
import os
import math 

res_path = 'inflation.npy'
model_dir = 'models/'
model_cache_size = 20


def blocking(p, ele, azi, origin=[0,0])
	point1, point2 = p['edges']
	height = p['height']

	intersection = geometry.ray_intersect([point1, point2], azi, origin)
	if not intersection:
		return False

	inter_height = math.tan(ele * math.pi / 180.) * \
					geometry.dist2d(intersection, [0, 0])

	if inter_height > height:
		return False

	return True


def los_degree(model, azi, ele):
	for plane in model:
		if blocking(model[plane], ele, azi):
			return 1
	return 0


def inflation(model, azi, ele):
	res = []
	for plane in model:
		point1, point2 = model[plane]['edges']
		mirror = geometry.mirror_point([point1, point2], [0,0])
		origin_mirror_inter = geometry.ray_intersect([point1, point2], mirror)
		if not origin_mirror_inter:
			continue

		blocked_other = False
		for plane2 in model:
			if plane2 == plane:
				continue 
			if blocking(model[plane2], ele, azi):
				blocked_other = True
				break

		if blocked_other:
			continue
		res.append(geometry.dist2d(origin_mirror_inter, [0,0]) / math.cos(ele * math.pi / 180.))

	if not res:
		return 0
	return sum(res) / float(len(res))


def offset_model(model, offset):
	for plane in model:
		model[plane]['edges'][0][0] += offset[0]
		model[plane]['edges'][0][1] += offset[1]
		model[plane]['edges'][1][0] += offset[0]
		model[plane]['edges'][1][1] += offset[1]
		
	return model


def load_model(lat, lon, model_cache):
	key = support.ll_to_str([lat, lon])
	if not key in model_cache:
		fpath = model_dir + '%s_b64.txt' % key
		if not os.path.exists(fpath):
			print('Cannot find %s' % fpath)
			return {}
		model_cache[key] = model_extract.read_model(fpath)

	if len(model_cache) > model_cache_size:
		keys = model_cache.keys()
		for k in keys:
			if k != key:
				del model_cache[k]
				break 

	return model_cache[key].copy()


def run(candidate_file):
	if not os.path.exists(candidate_file):
		print('Cannot find candidate_file!')
		sys.exist(0)

	inflation_wrapper = support.Wrapper(res_path)
	model_cache = {}
	fin = open(candidate_file, 'r').readlines()
	for line in fin:
		lat, lon, lat_sv, lon_sv = line.strip().split(',')
		model = load_model(lat_sv, lon_sv, model_cache)
		if not model:
			continue 
		
		pos_offset = geometry.relative_xy(map(float, [lat, lon]), map(float, [lat_sv, lon_sv]))	
		model = offset_model(model, pos_offset)

		for azi in range(0, 360):
			for ele in range(20, 80):
				los_deg = los_degree(model, azi, ele)
				if los_deg:
					inflation_wrapper.add(	float(lat), float(lon), azi, ele,
											[los_deg, inflation(model, azi, ele)]
										)
		break # TODO 

	inflation_wrapper.output()
	print('done')

