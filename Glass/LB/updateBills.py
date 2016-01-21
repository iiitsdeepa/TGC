import urllib2
import json
import logging
from time import sleep
from datetime import datetime, date, time
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.db import GqlQuery
from google.appengine.api import mail

bill_url = 'https://congress.api.sunlightfoundation.com/bills?fields=bill_id,official_title,popular_title,short_title,nicknames,keywords,summary_short,urls,history.active,history.vetoed,history.vetoed_at,history.enacted,history.enacted_at,sponsor_id,cosponsor_ids,cosponsor_count,keywords&%s&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
total_count = 0

bil = urllib2.urlopen(bill_url)
bill = bil.read()
billdata = json.loads(bill)

todaydate = datetime.today()
topdate = datetime.min
tempdate = GqlQuery("SELECT * FROM NationalDemocraticPrimary ORDER BY end_date DESC").get()
topdate = tempdate.end_date

#opening log file
congress = 114
billscsv = open('updatebills'+str(congress)+'.csv', 'w')
#cosponsorscsv = open('cosponsors'+str(congress)+'.csv', 'w')
#keywordscsv = open('keywords'+str(congress)+'.csv', 'w')

chambers=['hr','s']
for c in chambers:
	bill_method = 'congress=%d&bill_type=%s&per_page=20&page=%d' % (congress,c, 1)
	u = urllib2.urlopen(bill_url % bill_method)
	b = u.read()
	j = json.loads(b)
	ch = c
	total_count += int(j["count"])
	per_page = int(j["page"]["per_page"])
	num_pages = int(j["count"])/per_page
	print i, c, total_count,per_page,num_pages
	for x in range(1,num_pages+1):
		bill_method = 'congress=%d&bill_type=%s&per_page=20&page=%d' % (congress,ch, x)
		u = urllib2.urlopen(bill_url % bill_method)
		b = u.read()
		j = json.loads(b)
		#print json.dumps(j, indent=4)
		ra = j["results"]
		print 'page '+str(x)
		print bill_method
		for r in ra:
			try:
				bid = r["bill_id"].encode('utf-8')
			except:
				bid = '-1'
			try:
				official_title = r["official_title"].encode('utf-8')
			except:
				official_title = 'None'
			try:
				popular_title = r["popular_title"].encode('utf-8')
			except:
				popular_title = 'None'
			try:
				short_title = r["short_title"].encode('utf-8')
			except:
				short_title = 'None'
			try:
				nicknamesa = r["nicknames"].encode('utf-8')
				nicknames = '$$$'.join(nicknamesa)
			except:
		   		nicknames = 'None'
		   	url = r["urls"]["congress"].encode('utf-8')
		   	active = str(r["history"]["active"])
		   	vetoed = str(r["history"]["vetoed"])
		   	enacted = str(r["history"]["enacted"])
		   	sponsor = r["sponsor_id"].encode('utf-8')
		   	
		   	#parse for cosponsorscsv and keyowrdscsv
		   	"""try:
				keywordsa = r["keywords"]
				for k in iter(keywordsa):
					line = bid+','+k.encode('utf-8')+'\n'
					keywordscsv.write(line)
			except:
		   		keywords = 'None'
		   	try:
				cosponsorsa = r["cosponsor_ids"]
				for c in iter(cosponsorsa):
					line = bid+','+c.encode('utf-8')+'\n'
					cosponsorscsv.write(line)
			except:
		   		cosponsors = 'None'
		   	"""
		   	line = bid+'$$$'+official_title+'$$$'+popular_title+'$$$'+short_title+'$$$'+nicknames+'$$$'+url+'$$$'+active+'$$$'+vetoed+'$$$'+enacted+'$$$'+sponsor+'\n'
			billscsv.write(line)
		sleep(1.00)


print total_count

billscsv.close()
cosponsorscsv.close()
keywordscsv.close()