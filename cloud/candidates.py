from geometry import * 
from model_extract import * 
import os 
import math
from support import l2key

road_y = 12
road_x = 6
grid = 3
buf_size = 300

def gen_cand(x, y, direction):
	angle = math.atan2(y, x) + direction * math.pi / 180.
	length = math.sqrt(x * x + y * y)
	return [length * math.sin(angle), length * math.cos(angle)]


def run(model_file):
	model_data = open(model_file, 'r')
	temp = []
	fout = open('candidates.csv', 'w')

	cnt = 0
	for line in model_data:
		lat_sv, lon_sv, direction = line.strip().split(',')
		direction = float(direction)
		raw_file = 'models/%s,%s_b64.txt' % (lat_sv, lon_sv)
		if not os.path.exists(raw_file):
			continue 

		print('%d: %s' % (cnt, raw_file))
		cnt += 1

		for r in range(-road_x, road_x, grid):
			for w in range(-road_y, road_y, grid):
				offset = gen_cand(r, w, direction)
				lat, lon = xy2ll([lat_sv,lon_sv], offset)
				key = l2key(lat) + ',' + l2key(lon)
				if not key in temp:
					temp.insert(0, key)
					fout.write('%s,%s,%s,%s\n' % (lat, lon, lat_sv, lon_sv))
				if len(temp) > buf_size:
					temp.pop()

	fout.close()
	print('done')