import urllib2
import json



# opening the required url, and printing corresponding metadata
# input: url
# output: json data from url
def execute_url(url):
	# replace all space with ASIC II
	url = url.replace(" ", "%20")
	print "[alps_lib] executing the following url:"
	print "%s" % url

	# Send the GET request to the Place details service (using url from above)
	response = urllib2.urlopen(url)

	# Get the response and use the JSON library to decode the JSON
	json_raw = response.read()
	json_data = json.loads(json_raw)

	return json_data

def theta_to_heading(theta):
	heading = float(90) - float(theta)
	return heading

def heading_to_theta(heading):
	theta = float(90) - float(heading)
	return theta