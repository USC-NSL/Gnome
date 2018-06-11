import sys 
import numpy as np
import numpy as np
from support import * 
from localizer import Localizer

ll_m_ratio = 0.112214

class Gnome:
	def __init__(self, model_path):
		self.model = np.load(open(model_path, 'r')).item()
		self.head = 6
		self.payload = 6
		self.localizer = Localizer()
		print('Inflation model loaded')


	# head of data: Latitude, Longitude, Altitude, Speed, Accuracy, (UTC)TimeInMs
	# payload: Svid, Azi, Ele, SNR,	Used, EstPathInflation, ...
	def update(self, data):
		head = data[:6]
		lat, lon = l2key(data[0]), l2key(data[1])
		accuracy = data[4]
		lat_head, lat_body = l_break(lat)
		lon_head, lon_body = l_break(lon)

		if not lat_head in self.model or not lon_head in self.model[lat_head]:
			print('Not covered by model, use original location')
			return [lat, lon]

		search_rad = accuracy * 1.3 / ll_m_ratio
		candidates = {}
		for cand_lat_body in self.model[lat_head][lon_head]:
			if abs(lat_body - cand_lat_body) > search_rad:
				continue 
			candidates[cand_lat_body] = {}
			for cand_lon_body in self.model[lat_head][lon_head][cand_lat_body]:
				if abs(lon_body - cand_lon_body) > search_rad:
					continue 
				candidates[cand_lat_body][cand_lon_body] = \
						self.model[lat_head][lon_head][cand_lat_body][cand_lon_body]

		for cand_lat_body in candidates:
			for cand_lon_body in candidates[cand_lat_body]:
				for i in range(self.head, len(data), self.payload):
					azi, ele = map(int, data[i + 1 : i + 3])
					if ele in candidates[cand_lat_body][cand_lon_body][azi]:
						data[i + 5] = int(candidates[cand_lat_body][cand_lon_body][azi][ele])
				self.localizer.add_candidate(cand_lat_body, cand_lon_body, data)

		return self.localizer.update() 




'''
height = 181
width = 361
model = np.load(open(sys.argv[1], 'r')).item()
img = np.zeros((height,width,3), np.uint8)
# print(model)

max_ele = 0
for lat1 in model:
	for lon1 in model[lat1]:
		for lat2 in model[lat1][lon1]:
			for lon2 in model[lat1][lon1][lat2]:
				for azi in model[lat1][lon1][lat2][lon2]:
					for ele in model[lat1][lon1][lat2][lon2][azi]:
						img[height / 2 - ele, azi] = [255,255,255]
						if ele > max_ele:
							max_ele = ele

						
print(max_ele)
cv2.imwrite('res.png', img)
print('done')
'''