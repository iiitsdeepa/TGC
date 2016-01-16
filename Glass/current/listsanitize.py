import urllib2
import json
import re
from time import sleep

namelist_unsanitized = open('113namelist_unsanitized.csv', 'r')
namelist = open('113namelist', 'w')


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
		lname = clipper(a[2],'rando')
	else:
		fname = clipper(a[0],'rando')
		lname = clipper(a[1],'rando')
	names = fname+','+lname+','
	return names




for l in namelist_unsanitized:
	s = atLarge(l.split(' '))
	names = nameParse(s)
	#sanitize line (consolidate 2 part names, make districts numbers, remove spaces, and make legit csv line)
	if len(s) == 4:
		lname = clipper(s[0],'rando')
		fname = clipper(s[1],'rando')
		district = clipper(s[3],'district')
		nline = lname+','+fname+','+s[2]+','+district
		#print nline
	print names

namelist_unsanitized.close()
namelist.close()