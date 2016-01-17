#This file gets all active legislators and adds them to the Politician Table, as well as the terms. It is used to build the database, not append it

import urllib2
import json
from time import sleep

#finds and returns the first and last year a member has in office
def yearsInOffice(terms):
	fyio = 3000
	for term in terms:
		syear = int(term['start'][0:4])
		if syear <= fyio:
			fyio = syear
	return fyio

#trys to parse all social media links from the json
def socialMedia(pol):
	try:
		fbid = pol['results'][0]['facebook_id']
	except:
		fbid = 'None'
	try:
		twid = pol['results'][0]['twitter_id']
	except:
		twid = 'None'
	try:
		ywid = pol['results'][0]['youtube_id']
	except:
		ywid = 'None'
	return str(fbid), str(ywid), str(twid)

#sets the chamber, and then district or rank of a member of congress
def districtOrRank(pol):
	if pol['results'][0]['chamber'] == 'house':
		chamber = 'H'
		distrank = int(pol['results'][0]['district'])
	else:
		chamber = 'S'
		distrank = 'None'
		if ('True' == str(pol['results'][0]['in_office'])):
			rank = pol['results'][0]['state_rank']
			distrank = rank[0]
	return str(chamber), str(distrank)

#Tests to see what names this person has, filling in None for any wrong values
def convName(pol):
	try:
		last = str(pol['results'][0]['last_name'])
	except:
		last = 'None'
	try:
		first = str(pol['results'][0]['first_name'])
	except:
		first = 'None'
	try:
		middle = str(pol['results'][0]['middle_name'])
	except:
		middle = 'None'
	try:
		suffix = str(pol['results'][0]['name_suffix'])
	except:
		suffix = 'None'
	try:
		nickname = str(pol['results'][0]['nickname'])
	except:
		nickname = 'None'
	return str(last + "_" + first + "_" + middle + "_" + suffix + "_" + nickname)

def fecConv(ids):
	temp = ''
	for id1 in ids:
		temp += str(id1) + "_"
	temp = temp[:-1]
	return temp

#assigns values to each parameter and write it to the csv
def assignValues(pols, clog):
	in_office = str(pols["results"][0]["in_office"])
	party = str(pols["results"][0]["party"])
	gender = str(pols["results"][0]["gender"])
	state = str(pols["results"][0]["state"])
	state_name = str(pols["results"][0]["state_name"])
	chamber, distrank = districtOrRank(pols)
	birthday = str(pols["results"][0]["birthday"])
	fyio = yearsInOffice(pols["results"][0]["terms"])
	bioguide_id = str(pols["results"][0]["bioguide_id"])
	crp_id = str(pols["results"][0]["crp_id"])
	fec_ids = fecConv(pols["results"][0]["fec_ids"])
	name = convName(pols)
	phone = str(pols["results"][0]["phone"])
	website = str(pols["results"][0]["website"])
	contact_form = str(pols["results"][0]["contact_form"])
	facebook_id, youtube_id, twitter_id = socialMedia(pols)
	clog.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (in_office,party,gender,state,state_name,distrank,chamber,birthday,fyio,bioguide_id,crp_id,fec_ids,name,phone,website,contact_form,twitter_id,youtube_id,facebook_id))

#gets members of congress from set congress number using csv files
def getCongress(cnum):
	clog_fname = str(cnum) + 'Politicians.csv'
	clog = open(clog_fname, 'w')
	url = 'https://congress.api.sunlightfoundation.com/legislators?bioguide_id=%s&all_legislators=true&fields=in_office,party,gender,state,state_name,district,chamber,state_rank,birthday,terms.start,bioguide_id,crp_id,fec_ids,last_name,first_name,middle_name,nickname,name_suffix,phone,website,contact_form,twitter_id,youtube_id,facebook_id,&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
	membfilename = str(cnum) + '_bid_member.csv'
	mf = open(membfilename)
	num_pols = 1
	for l in iter(mf):
		l = l[:-1]
		bio,ln,fn = l.split(',')
		upols = urllib2.urlopen(url % (bio))
		pols = upols.read()
		jpols = json.loads(pols)
		print num_pols
		assignValues(jpols, clog)
		sleep(1.00)
		num_pols += 1
	clog.close()


getCongress(113)
