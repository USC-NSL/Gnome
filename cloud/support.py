import pickle
import gzip


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