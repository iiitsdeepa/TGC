#This file gets all active legislators and adds them to the Politician Table, as well as the terms. It is used to build the database, not append it

import urllib2
import json
import MySQLdb
from time import sleep

#connecting to the database
db = MySQLdb.connect(host="localhost", user="the_giver", passwd="memories", db="LegislativeBranch")
cursor = db.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

#sets the chamber, and then district or rank of a member of congress
def districtOrRank(pol):
	if pol['chamber'] == 'house':
		chamber = 'H'
		distrank = int(pol['district'])
	else:
		chamber = 'S'
		rank = pol['state_rank']
		distrank = rank[0]
	return chamber, distrank

#trys to parse all social media links from the json
def socialMedia(pol):
	try:
		fbid = pol['facebook_id']
	except:
		fbid = 'none'
	try:
		twid = pol['twitter_id']
	except:
		twid = 'none'
	return fbid, twid

#finds and returns the first and last year a member has in office
def yearsInOffice(terms):
	fyio = 3000
	lyio = 200
	for term in terms:
		syear = int(term['start'][0:4])
		eyear = int(term['end'][0:4])
		if syear <= fyio:
			fyio = syear
		if eyear > lyio:
			lyio = eyear
	return fyio, lyio

#inserts a dictionary of data into the database
def insertPol(p, A):
	sql = 'INSERT INTO Politician (bid,cid,gid,name,gender,bdate,fyio,lyio,state,distrank,chamber,party,active,fbid,twid,phone,website,contact_form,fax) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
	cursor.execute(sql,(p['bid'],p['cid'],p['gid'],p['name'],p['gender'],p['bdate'],p['fyio'],p['lyio'],p['state'],p['distrank'],p['chamber'],p['party'],A,p['fbid'],p['twid'],p['phone'],p['website'],p['contact_form'],p['fax']))

#inserts a term
def insertTerm(bid, congress):
	sql = 'INSERT INTO Terms (congress, politician_bid) VALUES (%s,%s)'
	cursor.execute(sql,(congress,bid))

#parses data for one politician and returns a dictionary of the parsed data
def parseData(pol):
	name = pol['first_name'] + '_' + pol['last_name']
	chamber,distrank = districtOrRank(pol)
	fbid,twid = socialMedia(pol)
	fyio,lyio = yearsInOffice(pol['terms'])
	try:
		fax = pol['fax']
	except:
		fax = 'none'
	p = {'bid':pol['bioguide_id'],'cid':pol['crp_id'],'gid':pol['govtrack_id'],'gender':pol['gender'],'bdate':pol['birthday'],'state':pol['state'],'chamber':chamber,'distrank':distrank,'party':pol['party'],'name':name,'active':'Y','fyio':fyio,'lyio':lyio,'fbid':fbid,'twid':twid,'phone':pol['phone'],'website':pol['website'],'contact_form':pol['contact_form'],'fax':fax}
	return p

def updateActive(p):
	sql = 'UPDATE Politician SET active=%s WHERE bid=%s'
	cursor.execute(sql,('A',p['bid']))	

#gets all current members of congress
def getCurrent(congress):
	i = 1
	numpages = 1
	num_pols = 0
	url = 'https://congress.api.sunlightfoundation.com/legislators?page=%s&per_page=50&fields=bioguide_id,govtrack_id,crp_id,first_name,last_name,gender,birthday,terms.start,terms.end,state,district,state_rank,chamber,party,twitter_id,facebook_id,phone,website,contact_form,fax,&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
	while i <= numpages+1:
		upols = urllib2.urlopen(url % i)
		pols = upols.read()
		jpols = json.loads(pols)
		#print json.dumps(jpols, indent=4, sort_keys=True)
		totalpols = jpols['count']
		perpage = 50
		numpages = totalpols / 50
		polarray = jpols['results']
		for pol in polarray:
			p = parseData(pol)
			insertPol(p, 'A')
			insertTerm(p['bid'], congress)
			num_pols+=1
		i+=1
	print totalpols,num_pols

#gets members of congress from set congress number using csv files
def getCongress(cnum):
	clog_fname = str(cnum) + '_bid_member.csv'
	clog = open(clog_fname, 'w')
	url = 'https://congress.api.sunlightfoundation.com/legislators?last_name=%s&first_name=%s&fields=bioguide_id,govtrack_id,crp_id,first_name,last_name,gender,birthday,terms.start,terms.end,state,district,state_rank,chamber,party,twitter_id,facebook_id,phone,website,contact_form,fax,&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
	membfilename = str(cnum) + 'membs.csv'
	mf = open(membfilename)
	num_pols = 0
	for l in iter(mf):
		l = l[:-1]
		ln,fn = l.split(',')
		upols = urllib2.urlopen(url % (ln,fn))
		pols = upols.read()
		jpols = json.loads(pols)
		#print json.dumps(jpols, indent=4, sort_keys=True)
		if jpols['count'] != 1:
			print (l, jpols['count'])
		else:
			p = parseData(jpols['results'][0])
			clog.write('%s,%s,%s\n' % (p['bid'],ln,fn))
			sql = 'SELECT bid FROM Politician WHERE bid = %s'
			cursor.execute(sql,(p['bid']))
			if cursor.fetchone()[0]:
				insertTerm(p['bid'],cnum)
			else:
				insertPol(p, cnum)
				insertTerm(p['bid'], cnum)
				num_pols+=1
		sleep(1.00)
	print num_pols
	clog.close()


getCongress(112)


#close 
cursor.close()
db.commit()
db.close()