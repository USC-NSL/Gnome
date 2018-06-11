# float array input to localizae algorithm (seperated by comma): 
'''
	Latitude,				# head: len=6
	Longitude,									
	Altitude,
	Speed,
	Accuracy,
	(UTC)TimeInMs, 		
	Svid,					# repeating payload:  			
	Azi,
	Ele,
	SNR,	
	Used,					# 1 means used 
	EstPathInflation,		# placeholder here
	ElapsedRealtimeMillis,	# this part from raw part of gnss logger
	TimeNanos,
	LeapSecond,
	TimeUncertaintyNanos,
	FullBiasNanos,
	BiasNanos,
	BiasUncertaintyNanos,
	DriftNanosPerSecond,
	DriftUncertaintyNanosPerSecond,
	HardwareClockDiscontinuityCount,
	Svid,
	TimeOffsetNanos,
	# State,
	ReceivedSvTimeNanos,
	ReceivedSvTimeUncertaintyNanos,
	Cn0DbHz,
	PseudorangeRateMetersPerSecond,
	PseudorangeRateUncertaintyMetersPerSecond,
	AccumulatedDeltaRangeState,
	AccumulatedDeltaRangeMeters,
	AccumulatedDeltaRangeUncertaintyMeters,
	CarrierFrequencyHz,
	CarrierCycles,
	CarrierPhase,
	CarrierPhaseUncertainty,
	MultipathIndicator,
	SnrInDb,
	# ConstellationType,
	AgcDb,
	CarrierFrequencyHz,
	# start of payload No.2..
'''

import os 
import sys 

# return format: {sv_no: [ele, azi, snr, if_used]}
def nmea_gsv(line, used_list):
	line = line.split('*')[0]
	data = line.split(',')
	i = 4
	res = {}
	while i < len(data):
		sv_no = int(data[i])
		res[sv_no] = []
		j = 1
		while j < 4: # ele, azi, snr
			if data[i + j] == '':
				res[sv_no].append(-1)
			else:
				res[sv_no].append(int(data[i + j]))
			j += 1
		if sv_no in used_list:
			res[sv_no].append(1)
		else:
			res[sv_no].append(0)
		i += 4	

	return res


# return format: {sv_no : [ele, azi, snr, if_used]}
# sv_no: 1-32 int
# ele: 0-90 int (-1 means no value)
# azi: 0-360 int (-1 means no value)
# snr: 0-99 int (-1 means no value)
# if_used: 1 for yes, 0 for no, int
def parse_nmea(lines):
	res = {}
	used_list = []
	for line in lines:
		if 'GPGSA' in line:
			data = line.split(',')
			for i in range(3, 15):
				if data[i] != '':
					used_list.append(int(data[i]))

	for line in lines:
		if 'GPGSV' in line:
			gsv_info = nmea_gsv(line, used_list)
			for i in gsv_info:
				res[i] = gsv_info[i]
	return res


class GPSmeta:
	def __init__(self, path=''):
		self.data = []
		self.cnt = 0
		if not path or not os.path.exists(path):
			print(path + ' not exist')
			return 

		log = open(path, 'r')
		line = log.readline()

		temp = []
		nmea = []
		while line != '':
			if '#' in line:
				line = log.readline()
				continue 
			d = line.strip()
			if 'Fix,gps,' in d:
				self.add(temp, nmea)
				temp = map(float, d[8:].split(','))

			elif 'NMEA,$' in d:
				nmea.append(d[6:])
				
			line = log.readline()

		self.add(temp, nmea)
		print('gps meta initiated')


	def add(self, header, nmea):
		if not header:
			return 

		nmea_dict = parse_nmea(nmea)

		for svid in nmea_dict:
			header += [svid]
			header += nmea_dict[svid]
			header += [-1]
		self.data.append(header)
		nmea = []
		header = []


	def read(self):
		if not self.data or self.cnt >= len(self.data):
			return ''
		self.cnt += 1
		return self.data[self.cnt - 1]


if __name__ == '__main__':
	# show what's extracted from logger file 
	meta = GPSmeta(sys.argv[1])
	head = 6
	payload = 6

	while True:
		data = meta.read()
		if not data:
			break 
		res = '[%f,%f](%f) - ' % (data[0], data[1], data[4])		# lat,lon,acc
		for i in range(head, len(data), payload):
			res += ' %f:(%f,%f)(%f)(%b)' % tuple(data[i : i + 5])		# svid, azi, ele, snr
		print(res)
		