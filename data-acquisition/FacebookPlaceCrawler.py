# FacebookPlaces.py
# Author: Kassio Machado - uOttawa/Canada and UFMG/Brazil | Sept. 2017
# This code by myself with strictly purpose of research.
# =============================================================================
# Code to seach the Instagram places indicated on photos on Facebook Graph API.
# The requests provide the name and gps coords of places and get (if available)
# a list of candidates/related correspondent places with the following fields:
# id, name, category, location, category_list, description, link

import sys
import time
import json
import numpy
import argparse
import colorama
import requests
import requests.exceptions
import datetime
from tqdm import tqdm

INFO = colorama.Fore.BLACK + colorama.Back.GREEN + '[INFO] '
WARNING = colorama.Fore.BLACK + colorama.Back.YELLOW + '[WRNG] '
ERROR = colorama.Fore.BLACK + colorama.Back.RED + '[ERROR] '
RESET = colorama.Fore.RESET + colorama.Back.RESET

if __name__ == "__main__":
    desc = 'Facebook Place Crawler - Explores the Facebook Places API.\
    It requires an input file formated as JSON with name to query and GPS \
    Coords. In addition a second file with Facebook OAuth credentials.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('app_index', default=0,
                        help='Index of app credentials on FacebookPlaces.json')
    parser.add_argument('inputfilename',
                        help='lines formated in JSON. Must provide place name \
                        to query and GPS coords')
    parser.add_argument('-i', '--interval', metavar='value',default=1,
                        help='Interval among requests (in seconds).')
    parser.add_argument('-c', '--config', metavar='filename',
                        default='FacebookPlaces.json',
                        help='File with OAuth credentials of Facebook API.')
    if len(sys.argv) == 1:
        parser.print_help()
        exit()
    else:
        args = parser.parse_args()

    inputfilename = args.inputfilename
    appIndex = int(args.app_index)
    interval = float(args.interval)
    configFilename = args.config

    inputfile = open(configFilename, 'r')
    appConfigs = json.load(inputfile)
    inputfile.close()

    defined = set()
    outputfilename = inputfilename.replace('.json', '-facebook.json')
    try:
        outputfile = open(outputfilename, 'r')
        for line in outputfile:
            if len(line) > 1:
                data = json.loads(line)
                defined.add(data['instagram'])
        outputfile.close()
        print INFO + str(len(defined)) + ' Places Defined Previously!' + RESET
    except IOError:
        print WARNING + 'File Previously Not Created!' + RESET
        pass
    outputfile = open(outputfilename, 'a', 0)

    inputfile = open(inputfilename, 'r')
    for nrows, l in tqdm(enumerate(inputfile), desc='Counting', leave=False):
        pass
    nrows += 1
    inputfile.seek(0)

    url =  'https://graph.facebook.com/search'
    tokens = appConfigs['apps'][appIndex]['app_id']
    tokens += "|" + appConfigs['apps'][appIndex]['app_secret']
    fields = 'id,name,category,location,category_list,description,link'

    for line in tqdm(inputfile, desc='Downloading',
                    total=nrows, dynamic_ncols=True):
        data = json.loads(line)
        if data['instagram'] in defined:
            continue
        payload = dict()
        payload['q'] = data['name']
        payload['type'] = 'place'
        payload['center'] = data['coords']
        payload['access_token'] = tokens
        payload['fields'] = fields
        try:
            resp = requests.get(url, params=payload)
        except requests.exceptions.ConnectionError, e:
            print ERROR + 'Connection error!' + RESET
            print e
            time.sleep(numpy.random.randint(55, 300)) # 1 to 5 minutes
            continue
        try:
            rjson = json.loads(resp.content)
        except ValueError: # invalid JSON
            continue
        try:
            del rjson['paging']
        except KeyError:
            pass
        data['facebook'] = rjson
        json.dump(data, outputfile)
        outputfile.write('\n')
        time.sleep(interval + numpy.random.rand())
    outputfile.close()
    inputfile.close()
