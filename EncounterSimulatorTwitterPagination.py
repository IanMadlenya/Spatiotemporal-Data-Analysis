# essentials
import csv
import sys
import math
import datetime
import pandas as pd
from tqdm import tqdm

def distanceCoords(lat1, long1, lat2, long2):
	try:
		# Convert latitude and longitude to
		# spherical coordinates in radians.
		degrees_to_radians = math.pi/180.0
		phi1 = (90.0 - lat1)*degrees_to_radians
		phi2 = (90.0 - lat2)*degrees_to_radians
		theta1 = long1*degrees_to_radians
		theta2 = long2*degrees_to_radians
		cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
			   math.cos(phi1)*math.cos(phi2))
		arc = math.acos( cos )
		return arc * 6373000.0 # return in meters
	except ValueError:
		return 0.01 # in case of very very very close

def loadTotalRows(inputfilename):
	inputfile = open(inputfilename, 'rb')
	for nrows, l in tqdm(enumerate(inputfile), desc='Counting Lines'):
		pass
	nrows += 1
	inputfile.close()
	return nrows

def loadNextPage(reader, samples=50000, datePattern='%Y-%m-%d %H:%M:%S'):
	eof = False
	samples = list()
	for i in tqdm(range(samples), desc='Loading CSV', leave=False):
		try:
			line = next(reader)
		except StopIteration:
			eof = True
		date_local, uid, lat, lng, id_data, country, content = line
		date_local = datetime.datetime.strptime(date_local, datePattern)
		samples.append((date_local, uid, float(lat), float(lng), id_data, country))
	return samples, eof

def loadTraceEncounters(inputfilename, maxInterval=900, maxDistance=150):

	bufferOut = list()
	outfilename = inputfilename.replace('.csv', '-encounters.csv')
	outf = open(outfilename, 'w')
	writer = csv.writer(outf)

	nrows = loadTotalRows(inputfilename)

	inputfile = open(inputfilename, 'r')
	reader = csv.reader(inputfile)
	eof = False

	pbar = tqdm(desc='Spatiotemporal Graph', total=nrows)
	while eof != True:
		trace, eof = loadNextPage(reader)
		for i, s1 in enumerate(trace):
			pbar.update(1)
			date_local, uid, lat, lng, id_data, country = s1
			# testing if all samples comparable to s1 are loaded in-memory
			s2 = trace[-1]
			interval = (s2[0] - date_local).total_seconds()
			if interval < maxInterval and eof != False:
				continue
			tmstmp = date_local.strftime('%y-%m-%d %H:%M:%S')
			for j in xrange(i + 1, len(trace)):
				s2 = trace[j]
				if uid != s2[1]:
					interval = (s2[0] - date_local).total_seconds()
					if interval <= maxInterval:
						dist = distanceCoords(lat, lng, s2[2], s2[3])
						if dist <= maxDistance:
							line = (tmstmp, uid, s2[1], int(interval), int(dist),  lat, lng, id_data, s2[4], country)
							bufferOut.append(line)
					else:
						break
				else:
					break
			if len(bufferOut) >= 5000:
				for row in bufferOut:
					writer.writerow(row)
				bufferOut = list()
		if eof == False:
			trace = trace[i+1:]
	for row in bufferOut:
		writer.writerow(row)

if __name__ == "__main__":
	args = sys.argv
	try:
		inputfile, maxInterval = args[1:]
		maxInterval = int(maxInterval)
	except IndexError:
		print '\n\n'
		print 'Please provide a valid cmd line'
		print 'ex: python EncounterSimulatorTwitter.py inputfile [t>0 secs]'
		print '\n\n'
		exit()

	loadTraceEncounters(inputfile, maxInterval)
