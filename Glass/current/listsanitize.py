import urllib2
import json
import re
from time import sleep

namelist_unsanitized = open('113namelist_unsanitized.csv', 'r')
namelist = open('113namelist.csv', 'w')


#helper function that clips commas, \n, and other things off the end of individual strings
def clipper(s, mode):
	ret = 'CLIPPERFAIL'
	i = len(s) -1
	if mode != 'district':
		if s[i] == ',' or s[i] =='\n' or s[i] == ' ':
			ret = s[:-1]
		else:
			ret = s
	if mode == 'district':
		ret = ''.join(x for x in s if x.isdigit())
	return ret

#helper function that tests for at large districts
def atLarge(a):
	ret = a
	if a[len(a) - 2] == 'At':
		newlist = []
		for i in range(0,len(a) - 1):
			if i != len(a) - 2:
				newlist.append(a[i])
			else:
				newlist.append('0')
		ret = newlist
	return ret

#helper function that gets only the first and last names from the list
def nameParse(a):
	if len(a) > 4:
		fname = clipper(a[0],'rando')
		lname = clipper(a[1],'rando')
	else:
		fname = clipper(a[0],'rando')
		lname = clipper(a[1],'rando')
	names = fname+','+lname+','
	return names

def parseAndWriteRepresentative(l):
	s = atLarge(l.split(' '))
	names = nameParse(s)
	state = s[len(s)-2]
	district = clipper(s[len(s)-1],'district')
	line = names + state+','+district
	print line
	namelist.write(line+'\n')

def parseAndWriteSenator(l):
	a = l.split('-')
	names = a[1].replace(' ',',')
	line = a[0]+','+names
	print line
	namelist.write(line)


senatortrip = 0
for l in namelist_unsanitized:
	if l == 'SENATORS\n':
		senatortrip = 1
		namelist.write('SENATORS\n')
		print l,'changing shit',senatortrip
		continue
	if senatortrip == 0:
		parseAndWriteRepresentative(l)
	else:
		parseAndWriteSenator(l)

namelist_unsanitized.close()
namelist.close()