import sys 
import pickle
import numpy as np
import support
import geometry 
import os

res_path = 'inflation.pkl'
model_dir = 'models/'
model_cache_size = 20


def inflation(model, azi, ele):
	# TODO
	# LOS degree 
	# path inflation
	return [0,0]
	pass


def offset_model(model, offset):
	return model

	
def load_model(lat, lon, model_cache):
	key = support.ll_to_str([lat, lon])
	if not key in model_cache:
		fpath = model_dir + '%s_b64.txt' % key
		if not os.path.exists(fpath):
			print('Cannot find %s' % fpath)
			return {}
		model_cache[key] = geometry.read_model(fpath)

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
				inflation_wrapper.add(	float(lat), float(lon), azi, ele,
										inflation(model, azi, ele)
									)
		break # TODO 

	inflation_wrapper.output()
	print('done')

