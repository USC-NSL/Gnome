import pickle
import gzip
import numpy as np


def l2key(l):
	return '%d' % int(l * 1000000)


def key2l(s):
	return float(s) / 1000000.


def ll_to_str(ll_):
	return (str(ll_[0]) + ',' + str(ll_[1]))


def str_to_ll(s):
	return map(float, s.split(','))


def save_zip(object, filename, protocol = 0):
		"""Saves a compressed object to disk
		"""
		file = gzip.GzipFile(filename, 'wb')
		file.write(pickle.dumps(object, protocol))
		file.close()


def l_break(l):
	s = l2key(l)
	return [int(s[:-4]), int(s[-4:])]


def load_zip(filename):
		"""Loads a compressed object from disk
		"""
		file = gzip.GzipFile(filename, 'rb')
		buffer = ""
		while True:
				data = file.read()
				if data == "":
						break
				buffer += data
		object = pickle.loads(buffer)
		file.close()
		return object


class Wrapper:
	def __init__(self, fname):
		self.fname = fname 
		self.data = {}

	def add(self, lat, lon, azi, ele, d):
		lat_head, lat_body = l_break(lat)
		lon_head, lon_body = l_break(lon)

		if not lat_head in self.data:
			self.data[lat_head] = {}
		if not lon_head in self.data[lat_head]:
			self.data[lat_head][lon_head] = {}

		if not lat_body in self.data[lat_head][lon_head]:
			self.data[lat_head][lon_head][lat_body] = {}
		if not lon_body in self.data[lat_head][lon_head][lat_body]:
			self.data[lat_head][lon_head][lat_body][lon_body] = {}			

		if not azi in self.data[lat_head][lon_head][lat_body][lon_body]:
			self.data[lat_head][lon_head][lat_body][lon_body][azi] = {}

		self.data[lat_head][lon_head][lat_body][lon_body][azi][ele] = d


	def output(self):
		print('saving model...')
		np.save(open(self.fname, 'w'), self.data)
		print('done')