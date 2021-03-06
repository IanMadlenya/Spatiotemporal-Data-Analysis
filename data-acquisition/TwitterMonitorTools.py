# -*- coding: utf-8 -*-
# ============================================================================================
# Kassio Machado - GNU Public License - 2017-07-01 Happy Canada Day
# PhD candidate on Science Computing - UFMG/Brazil
# ============================================================================================

import csv
import sys
import json
import numpy
import colorama
import datetime
from tqdm import tqdm
import TwitterMonitor

def exportStatsCountryPlaces(inputfiles):
	"""
	Count the samples and group them according to the places indicated by
	Twitter sample (not dependent of app - like Instagram of Foursquare). The
	method exports two CSV files for each input file containing the places and
	countries.
	"""
	for filename in inputfiles:
		dataPlaces, dataCountries = TwitterMonitor.loadPlaceStats(filename)
		outputfilename = filename.replace('.csv', '-countries.csv')
		print colorama.Fore.RED, 'Saving CSV countries\' file', filename, colorama.Fore.RESET
		writer = csv.writer(open(outputfilename, 'w'))
		writer.writerow(['country','samples'])
		for c in sorted(dataCountries.keys(), key=lambda k:dataCountries[k], reverse=True):
			writer.writerow([c, dataCountries[c]])

		outputfilename = filename.replace('.csv', '-places.csv')
		print colorama.Fore.RED, 'Saving CSV places\' file', outputfilename, colorama.Fore.RESET
		writer = csv.writer(open(outputfilename, 'w'))
		writer.writerow(['url','place_class', 'country', 'place_name', 'samples'])
		for p in sorted(dataPlaces.keys(), key=lambda k:dataPlaces[k][4], reverse=True):
			writer.writerow(dataPlaces[p])

def exportPlaceURL(inputfiles):
	"""
	Export samples' places info and URL
	independently of city and country.
	"""
	for filename in inputfiles:
		print colorama.Fore.RED, filename, colorama.Fore.RESET
		inputfile = open(filename, 'r')
		outputfile = open(filename.replace('.csv', '-url.csv'), 'w', 0)
		lineBuffer = list()
		invalidSample = 0
		for line in tqdm(inputfile, desc='Exporting URL\'s', disable=False):
			try:
				sample = eval(line.replace('\n', ''))
				id_data = sample['id_data'].encode('utf-8')
				id_user = sample['userid'].encode('utf-8')
				country = sample['country'].encode('utf-8')
				url = sample['urls'][-1]['expanded_url'].encode('utf-8')
				place_url = sample['place_url'].encode('utf-8')
				place_name = sample['place_name'].encode('utf-8')
				date_local = sample['date_local']
				lat = sample['lng']
				lng = sample['lat']
				line = id_data
				line += ',' + id_user
				line += ',' + country
				line += ',' + url.replace(',', '')
				line += ',' + place_url
				line += ',' + place_name.replace(',', ';')
				line += ',' + date_local.strftime('%y-%m-%d %H:%M:%S')
				line += ',' + lat
				line += ',' + lng
				line += '\n'
				lineBuffer.append(line)
				if lineBuffer >= 100000:
					for l in lineBuffer:
						outputfile.write(l)
					lineBuffer = list()
			except KeyError:
				invalidSample += 1
				continue
			except SyntaxError:
				invalidSample += 1
				continue
		for l in lineBuffer:
			outputfile.write(l)
		print '#' + str(invalidSample),'Invalid Samples'

# TODO: implement exportPlaceURLLegacy(inputfiles)

def exportPlaceURLByCountry(isoCodeCountry, inputfiles):
	"""
	Filters the fields and exports in CSV files the information related to the
	samples' venues, such as place name, place type, country, Twitter URL of place,
	and Instagram URL of the sample, according to the country code indicade
	according to the ISO Alpha-2
	"""
	print colorama.Fore.CYAN, 'Exporting files with URLs from', isoCodeCountry, colorama.Fore.RESET
	for filename in inputfiles:
		print colorama.Fore.RED, filename, colorama.Fore.RESET
		inputfile = open(filename, 'r')
		outputfile = open(filename.replace('.csv', '-url-' + isoCodeCountry.upper() + '.csv'), 'w')
		lineBuffer = list()
		invalidSample = 0
		for line in tqdm(inputfile, desc='Collecting URL\'s'):
			try:
				sample = eval(line.replace('\n', ''))
				country = sample['country'].upper()
				if country != isoCodeCountry:
					continue
				id_data = sample['id_data'].encode('utf-8')
				id_user = sample['userid'].encode('utf-8')
				country = sample['country'].encode('utf-8')
				url = sample['urls'][-1]['expanded_url'].encode('utf-8')
				place_url = sample['place_url'].encode('utf-8')
				place_name = sample['place_name'].encode('utf-8')
				date_local = sample['date_local']
				lat = sample['lng']
				lng = sample['lat']
				line = id_data
				line += ',' + id_user
				line += ',' + country
				line += ',' + url
				line += ',' + place_url
				line += ',' + place_name.replace(',', ';')
				line += ',' + date_local.strftime('%y-%m-%d %H:%M:%S')
				line += ',' + sample['lng']
				line += ',' + sample['lat']
				line += '\n'
				lineBuffer.append(line)
				if lineBuffer >= 25000:
					for l in lineBuffer:
						outputfile.write(l)
					lineBuffer = list()
			except KeyError:
				invalidSample += 1
				continue
			except SyntaxError:
				invalidSample += 1
				continue
		for l in lineBuffer:
			outputfile.write(l)

def exportPlaceURLByBoundBox(locationName, inputfiles, configFilename='TwitterMonitor.cfg'):
	"""
	Exports the files containing the URLs from samples locations according
	to Instagram. The function requires the pre-defined bounding box on
	TwitterMonitor.cfg.
	"""
	configparser = TwitterMonitor.loadConfigParser(configFilename)
	coords = TwitterMonitor.loadBoundBox(configparser, locationName)
	lng0, lngn = sorted([coords[0], coords[2]])
	lat0, latn = sorted([coords[1], coords[3]])
	print lat0, latn, lng0, lngn
	print colorama.Fore.CYAN, 'Exporting files with URLs from', locationName, colorama.Fore.RESET
	for filename in inputfiles:
		print colorama.Fore.RED, filename, colorama.Fore.RESET
		inputfile = open(filename, 'r')
		outputfile = open(filename.replace('.csv', '-url-' + locationName.upper() + '.csv'), 'w')
		lineBuffer = list()
		invalidSample = 0
		for line in tqdm(inputfile, desc='Exporting URL\'s', disable=True):
			try:
				sample = eval(line.replace('\n', ''))
				lng = float(sample['lat'])
				lat = float(sample['lng'])
				if lat >= lat0 and lat <= latn and lng >= lng0 and lng <= lngn:
					id_data = sample['id_data'].encode('utf-8')
					id_user = sample['userid'].encode('utf-8')
					country = sample['country'].encode('utf-8')
					url = sample['urls'][-1]['expanded_url'].encode('utf-8')
					place_url = sample['place_url'].encode('utf-8')
					place_name = sample['place_name'].encode('utf-8')
					date_local = sample['date_local']
					lat = sample['lng']
					lng = sample['lat']
					line = id_data
					line += ',' + id_user
					line += ',' + country
					line += ',' + url.replace(',', '')
					line += ',' + place_url
					line += ',' + place_name.replace(',', ';')
					line += ',' + date_local.strftime('%y-%m-%d %H:%M:%S')
					line += ',' + sample['lng']
					line += ',' + sample['lat']
					line += '\n'
					lineBuffer.append(line)
					if lineBuffer >= 1000:
						for l in lineBuffer:
							outputfile.write(l)
						lineBuffer = list()
			except KeyError:
				invalidSample += 1
				continue
			except SyntaxError:
				invalidSample += 1
				continue
		for l in lineBuffer:
			outputfile.write(l)
		print '#' + str(invalidSample) + ' invalid samples ' + filename

def exportPlaceURLByBoundBoxLegacy(locationName, inputfiles,
									configFilename='TwitterMonitor.cfg',
									datePattern='%Y-%m-%d %H:%M:%S'):
	"""
	Exports the files containing the URLs from samples locations according
	to Instagram legacy datasets.
	The function requires the pre-defined bounding box on
	TwitterMonitor.cfg.
	"""
	configparser = TwitterMonitor.loadConfigParser(configFilename)
	coords = TwitterMonitor.loadBoundBox(configparser, locationName)
	lng0, lngn = sorted([coords[0], coords[2]])
	lat0, latn = sorted([coords[1], coords[3]])
	print lat0, latn, lng0, lngn
	print colorama.Fore.CYAN, 'Exporting files with URLs from', locationName, colorama.Fore.RESET
	for filename in inputfiles:
		print colorama.Fore.RED, filename, colorama.Fore.RESET
		if '.dat' not in filename:
			print 'Please check the extesion of input file (require .dat)'
			exit()
		inputfile = open(filename, 'r')
		outputfile = open(filename.replace('.dat', '-url-' + locationName.upper() + '.csv'), 'w')
		lineBuffer = list()
		invalidSample = 0
		for line in tqdm(inputfile, disable=True):
			try:
				# sample = eval(line.replace('\n', ''))
				sample = line.split(', ')
				if len(sample) != 8:
					invalidSample += 1
					continue
				lng = float(sample[2])
				lat = float(sample[3])
				if lat >= lat0 and lat <= latn and lng >= lng0 and lng <= lngn:
					id_data = sample[0].encode('utf-8')
					id_user = sample[1].encode('utf-8')
					country = 'None'
					place_url = 'None'
					place_name = sample[5].encode('utf-8')
					date_local = datetime.datetime.strptime(sample[4], datePattern)
					tweet = sample[6].encode('utf-8').split(' ')
					url = None
					for x in tweet[::-1]:
						if 'https://t.co' in x:
							url = x
							break
					if url == None:
						invalidSample += 1
						continue
					line = id_data
					line += ',' + id_user
					line += ',' + country
					line += ',' + url.replace(',', '')
					line += ',' + place_url
					line += ',' + place_name.replace('  ', '; ')
					line += ',' + date_local.strftime('%y-%m-%d %H:%M:%S')
					line += ',' + sample[3]
					line += ',' + sample[2]
					line += '\n'
					lineBuffer.append(line)
					if lineBuffer >= 1000:
						for l in lineBuffer:
							outputfile.write(l)
						lineBuffer = list()
			except KeyError:
				invalidSample += 1
				continue
			except SyntaxError:
				invalidSample += 1
				continue
		for l in tqdm(lineBuffer, desc='Saving CSV'):
			outputfile.write(l)
		print '#' + str(invalidSample) + ' invalid samples ' + filename

def mergePlaceDataset(filenameUrl, filenameResolved, outputfilename=None):
	"""
		Merges the original URL dataset with the resolved information obtained
		with InstagramPlaceCrawler from place (name and url) and login user.
	"""
	unavailable = 'not-available'
	dataResolved = dict()
	inputfileResolved = open(filenameResolved, 'r')
	for line in inputfileResolved:
		sample = line.split(',') # sample_id, instagram_url, instagram_place, name_place, user_name
		if sample[4] != unavailable:
			sample[4] = sample[4].replace('\n', '')
			dataResolved[sample[0]] = sample[2] + ',' + sample[3] + ',' + sample[4]

	if outputfilename == None:
		outputfilename = filenameResolved.replace('resolved', 'merged')
		if 'merged.csv' not in outputfilename:
			print 'Error on outputfile name'
			return
	outputfile = open(outputfilename, 'w')
	inputfileUrl = open(filenameUrl, 'r')
	print filenameUrl
	for line in inputfileUrl:
		sample = line.split(',')
		try:
			infoResolved = dataResolved[sample[0]]
		except KeyError:
			infoResolved = 'not-available,not-available,not-available'
		data = line[:-1] + ',' + infoResolved + '\n'
		outputfile.write(data)

def validateFiles(inputfiles):
	'''
		Validates the files exported from export methods (original files with urls),
		the resolved url files and the merged files.
	'''
	for filename in inputfiles:
		inputfile = open(filename, 'r')
		corruptLines = 0
		dateFormat = '%y-%m-%d %H:%M:%S'
		if '-resolved.csv' in filename:
			print colorama.Fore.BLUE + filename + colorama.Fore.RESET
			for line in inputfile:
				fields = line.split(',')
				if len(fields) != 5:
					corruptLines += 1
				int(fields[0])
				if 'http' not in fields[1]:
					raise Exception('Invalid photo URL: ' + line)
				elif 'http' not in fields[2] and fields[2] != 'not-available':
					raise Exception('Invalid place URL: ' + line)
		elif '-merged.csv' in filename:
			print colorama.Fore.RED + filename + colorama.Fore.RESET
			for line in inputfile:
				fields = line.split(',')
				if len(fields) != 12:
					corruptLines += 1
				try:
					int(fields[0])
					int(fields[1])
				except ValueError:
					# print 'Invalid ids:', line
					continue
				try:
					float(fields[7])
					float(fields[8])
				except ValueError:
					print 'Invalids coords:', line
					continue
				try:
					datetime.datetime.strptime(fields[6], dateFormat)
				except ValueError:
					print 'Invalid datetime:', line
					continue

				if 'http' not in fields[3]:
					raise Exception('Invalid photo URL: ' + line)
				elif 'http' not in fields[9] and fields[9] != 'not-available':
					raise Exception('Invalid place URL: ' + line)
		else:
			print colorama.Fore.YELLOW + filename + colorama.Fore.RESET
			for line in inputfile:
				fields = line.split(',')
				if len(fields) != 9:
					corruptLines += 1
				try:
					int(fields[0])
					int(fields[1])
				except ValueError:
					print 'Invalid ids:', line
					continue
				try:
					float(fields[7])
					float(fields[8])
				except ValueError:
					print 'Invalids coords:', line
					continue
				try:
					datetime.datetime.strptime(fields[6], dateFormat)
				except ValueError:
					print 'Invalid datetime:', line
					continue
				if 'http' not in fields[3]:
					raise Exception('Invalid photo URL: ' + line)
		if corruptLines > 0:
			print '#' + str(corruptLines) + ' corrupted lines ' + filename
	return None

def exportInstagramPlaces(inputfilenames, city):
	'''
		Export the places indicated on tweets. Focused in instagram samples.
		The output is a file formated as a JSON object in each line.
	'''
	# 743438664911335424, 	id_data
	# 308749176, 			userid
	# US,					country
	# https://www.instagram.com/p/BGsZetZngc9/,
	# https://api.twitter.com/1.1/geo/id/1d9a5370a355ab0c.json,
	# Chicago; IL,
	# 16-06-16 13:42:44,
	# 41.88256075,
	# -87.623115,
	# https://www.instagram.com/explore/locations/96446262/the-giant/,
	# The Giant,
	# _dancingincircles_

	dictPlaces = dict()
	for inputfilename in inputfilenames:
		inputfile = open(inputfilename, 'r')
		print 'Reading', inputfilename
		for line in tqdm(inputfile, desc='Loading', leave=False):
			fields = line.split(',')
			country = fields[2]
			instagram = fields[9]
			if instagram == 'not-available':
				continue
			name = fields[10]
			placeid = fields[7] + ',' + fields[8]
			data = dict(name=name, instagram=instagram)
			try:
				coords = dictPlaces[instagram]['coords']
				try:
					coords[placeid] += 1
				except KeyError:
					coords[placeid] = 1
			except KeyError:
				data['coords'] = {placeid:1}
				dictPlaces[instagram] = data
			dictPlaces[instagram]['country'] = country
	sortedPlaces = sorted(dictPlaces.keys(), key=lambda k:sum(dictPlaces[k]['coords'].values()), reverse=True)
	outputfilename = city + '-places-database.json'
	outputfile = open(outputfilename, 'w')
	for p in sortedPlaces:
		data = dictPlaces[p]
		coords = data['coords']
		if len(coords) == 1: # 1 coord 1 single sample
			data['coords'] = data['coords'].keys()[0]
		elif sum(coords.values()) > len(coords):
			sortedCoords = sorted(coords.keys(), key=lambda k:coords[k], reverse=True)
			data['coords'] = sortedCoords[0]
		else:
			data['coords'] = numpy.random.choice(data['coords'].keys())
		json.dump(data, outputfile)
		outputfile.write('\n')
	outputfile.close()
	return

if __name__ == "__main__":
	args = sys.argv[1:]
	f = args.pop(0)
	if f == 'stats':
		exportStatsCountryPlaces(args)
	elif f == 'url':
		inputfiles = args
		exportPlaceURL(inputfiles)
	elif f == 'url-country':
		isoCodeCountry = args.pop(0)
		inputfiles = args
		exportPlaceURLByCountry(isoCodeCountry, inputfiles)
	elif f == 'url-bbox':
		locationName = args.pop(0)
		inputfiles = args
		exportPlaceURLByBoundBox(locationName, inputfiles)
	elif f == 'url-bbox-legacy':
		locationName = args.pop(0)
		inputfiles = args
		exportPlaceURLByBoundBoxLegacy(locationName, inputfiles)
	elif f == 'merge-url':
		if len(args) == 3:
			furl, fresolved, fout = args
			mergePlaceDataset(furl, fresolved, fout)
		else:
			furl, fresolved = args
			mergePlaceDataset(furl, fresolved)
	elif f == 'validate-url-files':
		inputfiles = args
		validateFiles(inputfiles)
	elif f == 'places-db':
		city = args.pop(0)
		inputfilenames = args
		exportInstagramPlaces(inputfilenames, city)
	else:
		print 'look in the code to know the CLI haha :)'






#
