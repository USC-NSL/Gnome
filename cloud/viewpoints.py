import os

area_file = 'alps/config/query_area.info'
dst_file = 'hehe.txt'

def run(area_boundary):
	fout = open(area_file, 'w') 
	print(area_boundary)
	fout.write('%f, %f, %f, %f' % tuple(area_boundary))
	fout.close()

	print('query region: %s' % `area_boundary`)

	print('------------ generate_initial_point ------------')
	os.system('python alps/01.generate_initial_point.py')
	
	print('------------ generate_standing_point ------------')
	os.system('python alps/02.generate_standing_point.py')
	
	print('------------ gtGPS ------------')
	os.system('python alps/03.gtGPS.py')
	
	print('------------ adjust_standing_point ------------')
	os.system('python alps/04.adjust_standing_point.py')
	
	print('viewpoints generated')

