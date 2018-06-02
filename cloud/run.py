import sys 
import viewpoints
# import model
# import candidates
# import path_inflation

if __name__ == '__main__':
	if len(sys.argv) < 5:
		print('Wrong argv! Should be \'$python run.py lat_top lat_bot lon_left lon_right\'')
		sys.exit(0)

	print('====== generating SV viewpoints ======')
	viewpoints.run(map(float, sys.argv[1:]))
	print('====== generating 3D model ======')
	# model_path = model.run('viewpoints.txt')
	print('====== generating candidates ======')
	# candidate_path = candidates.run(sv_viewpoints_path, model_path)
	print('====== computing path inflation ======')
	# path_inflation.run(candidate_path, model_path)
	print('done')
