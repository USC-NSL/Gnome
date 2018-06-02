from libs import alps_lib
import math

class node():
	def __init__(self, lat, lng, theta = 0):
		self.lat = float(lat)
		self.lng = float(lng)
		self.theta = float(theta)

class area():
	def __init__(self, lat1, lng1, lat2, lng2):
		self.lat1 = float(lat1)
		self.lng1 = float(lng1)
		self.lat2 = float(lat2)
		self.lng2 = float(lng2)

def check_node_within_area(query_area, tmp):
	if (tmp.lat > query_area.lat1 and tmp.lat < query_area.lat2 and tmp.lng > query_area.lng1 and tmp.lng < query_area.lng2):
		return True
	else:
		return False

# instead of convert it into x-y plane, here we calculate theta in lat-lng directly
def get_theta(origin, destination):
	theta = math.atan2(destination.lat - origin.lat, destination.lng - origin.lng) * 180 / math.pi
	return theta

def calculate_distance_in_degree(origin, destination):
	delta_lat = origin.lat - destination.lat
	delta_lng = origin.lng - destination.lng

	result = math.sqrt(delta_lat * delta_lat + delta_lng * delta_lng)

	return result

# ====== main =====
if __name__ == '__main__':

	# read the city you want to query
	query_city = open("./alps/config/query_city.info", "r").readline().rstrip()
	# read the area you want to query
	# format for area
	# lat-lng of lower-left point, lat-lng of upper-right point
	query_area = open("./alps/config/query_area.info", "r").readline().rstrip()

	work_dir = "./alps/data/%s/%s/" % (query_city, query_area.replace(" ", "").replace(",", "|"))

	f_input = open(work_dir + "01.generate_initial_point_output.txt", "r")
	f_output = open(work_dir + "02.generate_standing_point_output.txt", "w")

	f_hacking = open(work_dir + "02.gps_hacking_input.txt", "w")

	tmp = query_area.replace(" ", "").split(",")
	query_area = area(tmp[0], tmp[1], tmp[2], tmp[3])

	way_index = 0
	while (f_input.readline()):
		way_id = f_input.readline().rstrip()
		initial_point_num = int(f_input.readline().rstrip())
		initial_point_array = []
		for i in range(initial_point_num):
			tmp = f_input.readline().rstrip().split(",")
			tmp_lat = tmp[0]
			tmp_lng = tmp[1]
			tmp_node = node(tmp_lat, tmp_lng)
			initial_point_array.append(tmp_node)

		node_num = 0
		standing_point_array = []

		# deal with the first initial_point_num - 1 points
		for i in range(initial_point_num - 1):
			# head node
			origin = initial_point_array[i]
			# tail node
			destination = initial_point_array[i + 1]

			# calculate theta angle that is perpendicular to
			# the line from origin to destination
			# rememeber to add "90" here!
			theta = get_theta(origin, destination) + 90

			tmp_node = node(origin.lat, origin.lng, theta)
			if check_node_within_area(query_area, tmp_node):
				standing_point_array.append(tmp_node)
				node_num += 1

			# generate a series of node between origin and destination
			distance_in_degree = calculate_distance_in_degree(origin, destination)
			distance_step = int(distance_in_degree * 10000) + 1 # similar to distance_in_degree % 0.0001

			delta_lat = destination.lat - origin.lat
			delta_lng = destination.lng - origin.lng

			for j in range(1, distance_step):
				tmp_lat = origin.lat + j * delta_lat / distance_step
				tmp_lng = origin.lng + j * delta_lng / distance_step

				# nodes between origin and destination can re-use theta
				tmp_node = node(tmp_lat, tmp_lng, theta)
				if check_node_within_area(query_area, tmp_node):
					standing_point_array.append(tmp_node)
					node_num += 1

		# deal with the last point (the last point has no next point...)
		origin = initial_point_array[initial_point_num - 2]
		destination = initial_point_array[initial_point_num - 1]

		theta = get_theta(origin, destination) + 90
		tmp_node = node(destination.lat, destination.lng, theta)
		if check_node_within_area(query_area, tmp_node):
			standing_point_array.append(tmp_node)
			node_num += 1

		# print to f_output
		f_output.write("=== play with the %dth way ===\n" % way_index)
		f_output.write("%s\n" % way_id)
		f_output.write("%d\n" % node_num)

		for i in range(node_num):
			tmp_node = standing_point_array[i]
			f_output.write("%s,%s\n" % (tmp_node.lat, tmp_node.lng))
			f_output.write("%s\n" % tmp_node.theta)

			# print "%s,%s" % (tmp_node.lat, tmp_node.lng)
			f_hacking.write("%s,%s\n" % (tmp_node.lat, tmp_node.lng))

		way_index += 1


