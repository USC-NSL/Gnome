from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
import numpy as np
import argparse
import cv2


class SkyDetector:
	def __init__(self):
		print('SkyDetector initiated')


	def detect(self, image):
		shifted = cv2.pyrMeanShiftFiltering(image, 21, 51)
		gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
		thresh = cv2.threshold(gray, 0, 255,
			cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
		D = ndimage.distance_transform_edt(thresh)
		localMax = peak_local_max(D, indices=False, min_distance=20,
			labels=thresh)
		labels = watershed(-D, markers, mask=thresh)

		res = []
		for x in range(len(labels[0])):
			skyline = len(labels) - 1
			for y in range(len(labels) - 1):
				if labels[y][x] and not labels[y + 1][x]:
					skyline = y
					break 
			res.append(skyline)
		return res