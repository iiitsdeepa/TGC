#pulled up to N00033492

import urllib2
import json
from time import sleep

f = open('crpbase.txt', 'r')

candsector_url = 'http://www.opensecrets.org/api/?method=candSector&output=json&cid=%s&cycle=2014&apikey=ef5e75a0fc095fa58238c4ffb40d29f1'
candind_url = 'http://www.opensecrets.org/api/?method=candIndustry&output=json&cid=%s&cycle=2014&apikey=ef5e75a0fc095fa58238c4ffb40d29f1'
candcontrib_url = 'http://www.opensecrets.org/api/?method=candContrib&output=json&cid=%s&cycle=2014&apikey=ef5e75a0fc095fa58238c4ffb40d29f1'

log_file = open('pull_finances.txt', 'w')
i = 0
while i < 398:
	#read in data from file
	x = f.readline()
	if not x:
		break
	cid, n, d = x.split(',')
	district = d[0] + d[1] + '_' + d[2] + d[3]

	#use data to get top 10 contributers
	print cid
	ucontrib = urllib2.urlopen(candcontrib_url % cid)
	contrib = ucontrib.read()
	jcontrib = json.loads(contrib)

	contributors = jcontrib['response']['contributors']['contributor']
	cstring = ''
	for c in contributors:
		org_name = c['@attributes']['org_name']
		total = c['@attributes']['total']
		single_cstring = '%s,%s;' % (org_name, total)
		cstring = cstring + single_cstring

	#print to file
	print cid, n, district, cstring
	log_file.write('%s::%s::%s::%s\n' % (cid, n, district, cstring))
	i = i + 1
	sleep(1.00)
	
