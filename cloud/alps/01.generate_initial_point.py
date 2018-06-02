from libs import alps_lib
import os

# ====== main =====
if __name__ == '__main__':

	# read the city you want to query
	query_city = open("./alps/config/query_city.info", "r").readline().rstrip()
	# read the area you want to query
	# format for area
	# lat-lng of lower-left point, lat-lng of upper-right point
	query_area = open("./alps/config/query_area.info", "r").readline().rstrip()

	work_dir = "./alps/data/%s/%s/" % (query_city, query_area.replace(" ", "").replace(",", "|"))
	if not os.path.exists(work_dir):
		os.makedirs(work_dir)

	f_output = open(work_dir + "01.generate_initial_point_output.txt", "w")

	# generate the RESTful url to fetch json data from OpenStreetMap/Overpass
	query = "[out:json];way[\"highway\"~\"primary|secondary|tertiary|residential\"](%s);out geom;" % query_area
	url = "http://overpass-api.de/api/interpreter?data=%s" % query

	json_data = alps_lib.execute_url(url)

	if (json_data is None):
		print "Error!"
	else:
		way_index = 0
		for element in json_data["elements"]:
			if (element["type"] == "way"):
				f_output.write("=== play with the %dth way ===\n" % way_index)
				f_output.write("%s\n" % element["id"])
				f_output.write("%d\n" % len(element["geometry"]))
				for node in element["geometry"]:
					lat = str(node["lat"])
					lng = str(node["lon"])
					f_output.write("%s,%s\n" % (lat, lng))

				way_index += 1
