import sys 
import os
import model_extract

dst_dir = 'models/'
model_file = 'models.csv'

def run(viewpoints_file):
	if not os.path.exists(viewpoints_file):
		print('Cannot find viewpoints_file!')
		sys.exist(0)

	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)

	viewpoints_data = open(viewpoints_file, 'r').readlines()
	
	fout = open(model_file, 'w')

	for line in viewpoints_data:
		vp = line.strip()
		direction = model_extract.download(vp.split(','), dst_dir)
		fout.write(vp + ',' + str(direction) + '\n')

	fout.close()	
	print('done')


