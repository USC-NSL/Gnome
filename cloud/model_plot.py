# drawer by xc
# used for visualization of depth info 

import scipy.misc as smp
from geometry import *
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches


MAX_DISTANCE = 200
WIDTH = 512
HEIGHT = 256

SNR = ['#993333', '#ff0000', '#ff9933', '#ffff00', '#33cc33']
SNR_THRES = [0, 5, 10, 15, 20]

colors = [	[64,64,0], [0,64,64], [64,0,64], 
			[128,128,0], [0,128,128], [128,0,128], [0,64,128],
			[64,128,0], [0,128,64], [128,0,64], [0,128,64]]


class BmpDrawer:
	def __init__(self, width, height, imgname):
		self.data = np.zeros((height, width, 3), dtype=np.uint8)
		self.path = imgname

	def draw(self, x, y, color):
		self.data[y, x] = color

	def show_img(self):
		img = smp.toimage(self.data)
		img.show()

	def save_img(self):
		img = smp.toimage(self.data)
		img.save(self.path)


def get_color(planeId, voxel, mode, para):
	if mode == 'selected':
		if planeId in para:
			return [0,255,0]
		return [0,0,255]
		
	if mode == 'planes':
		return colors[planeId % len(colors)]

	if mode == 'points':
		pix_dist = 255 - 255 * voxel.pos.distance() / MAX_DISTANCE
		if pix_dist < 0:
			return [0, 0, 0]
		return [pix_dist, pix_dist, pix_dist]


def snr_color(snr):
	clr = SNR[0]
	if snr > SNR_THRES[0]:
		clr = SNR[1]
	if snr > SNR_THRES[1]:
		clr = SNR[2]
	if snr > SNR_THRES[2]:
		clr = SNR[3]
	if snr > SNR_THRES[3]:
		clr = SNR[4]
	return clr 


def azel_to_pix(azi, ele):
	wid = azi / TWO_PI * (WIDTH - 1)
	hei = ele / PI * (HEIGHT - 1)
	return wid, hei


def save_image(imgname, voxels, mode, para=[]):
	drawer = BmpDrawer(WIDTH, HEIGHT, imgname)
	for planeId in voxels:
		for voxel in voxels[planeId]:
			drawer.draw(voxel.azi, voxel.ele, get_color(planeId, voxel, mode, para))	
	drawer.save_img()


def add_point(imgname, pos, pos_type='azel', color='w', marker='*', markersize=15, text=''):
	azi = pos[0]
	ele = pos[1]
	if pos_type == 'xyz':
		azi, ele = to_azi_ele(pos[0], pos[1])

	wid, hei = azel_to_pix(azi, ele)
	plt.plot(wid, hei, color=color, marker=marker, markersize=markersize)
	plt.text(wid-8, hei+5, text, color='blue', fontsize=10)


def add_hull(imgname, hull):
	for line in hull:
		plt.plot([line[0].azi, line[1].azi], [line[0].ele, line[1].ele], '-r',linewidth=2)


def load_img(imgname):
	im = plt.imread(imgname)	# visualize the boundaries
	plt.imshow(im)


def show_img():
	plt.show()


def legend():
	star = mlines.Line2D([], [], color='white', marker='*', markersize=15)
	sv = mlines.Line2D([], [], color='yellow', marker='o', markersize=15)
	
	plt.legend([star, sv], ['Receiver', 'Color:SNR, Number:SV#'])