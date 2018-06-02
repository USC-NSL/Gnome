# ====== main =====
if __name__ == '__main__':

	# read the city you want to query
	query_city = open("./alps/config/query_city.info", "r").readline().rstrip()
	# read the area you want to query
	# format for area
	# lat-lng of lower-left point, lat-lng of upper-right point
	query_area = open("./alps/config/query_area.info", "r").readline().rstrip()

	work_dir = "./alps/data/%s/%s/" % (query_city, query_area.replace(" ", "").replace(",", "|"))

	f_input = open(work_dir + "02.generate_standing_point_output.txt", "r")
	f_hack = open(work_dir + "03.gps_hacking_output.txt", "r")
	# f_output = open(work_dir + "04.adjust_standing_point_output.txt", "w")
	f_output = open("viewpoints.txt", "w")

	way_index = 0

	while (f_input.readline()):
		way_id = f_input.readline().rstrip()
		node_num = int(f_input.readline().rstrip())

		# print to f_output
		# f_output.write("=== play with the %dth way ===\n" % way_index)
		# f_output.write("%s\n" % way_id)
		# f_output.write("%d\n" % node_num)

		for i in range(node_num):
			old_gps = f_input.readline().rstrip()
			theta = f_input.readline().rstrip()
			new_gps = f_hack.readline().rstrip().replace(" ", "")
			if 'Error' in new_gps:
				continue 

			print "%s -> %s" % (old_gps.ljust(30), new_gps)
			f_output.write("%s\n" % new_gps)

			# f_output.write("%s\n" % theta)

		way_index += 1

