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

#opening log file
congress = 114
topdate = datetime.strptime('2016-01-01T16:55:00Z', '%Y-%m-%dT%H:%M:%SZ')#datetime.min
tempdate = GqlQuery("SELECT voted_at FROM NationalDemocraticPrimary ORDER BY voted_at DESC").get()
topdate = datetime.strptime(tempdate.voted_at, '%Y-%m-%dT%H:%M:%SZ')

chambers=['house','senate']
bill_url = 'https://congress.api.sunlightfoundation.com/votes?congress=%s&chamber=%s&per_page=50&%s&fields=voter_ids,bill_id,roll_id,congress,voted_at,vote_type,roll_type,question,required,result,source,breakdown&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
total_count = 0
for c in chambers:
	u = urllib2.urlopen(bill_url % (congress, c,'page=1'))
	b = u.read()
	j = json.loads(b)

	total_count += int(j["count"])
	per_page = int(j["page"]["per_page"])
	num_pages = int(j["count"])/per_page
	print j["count",per_page,num_pages
	breakvar = False
	for x in range(1,num_pages+1):
		page = 'page='+str(x)
		u = urllib2.urlopen(bill_url % (congress, c, page))
		b = u.read()
		j = json.loads(b)
		ra = j["results"]
		print 'page '+str(x)
		for r in ra:

			try:
				bid = str(r["bill_id"])
			except:
				continue
			try:
				rid = str(r["roll_id"])
			except:
				rid = 'None'
			"""for bioguide_id, vote in r['voter_ids'].items():
				if (vote == 'Yea'):
					vote = 'Y'
				elif (vote == 'Nay'):
					vote = 'N'
				elif (vote == 'Not Voting'):
					vote = 'NV'
				elif (vote == 'Present'):
					vote = 'P'
				else:
					vote = 'O'
				cilog.write('%s,%s,%s,%s\n' % (bid, rid, bioguide_id, vote))
			"""
			congress = str(r["congress"])
			voted_at = str(r["voted_at"])
			vote_type = str(r["vote_type"])
			roll_type = str(r["roll_type"])
			roll_type = roll_type.replace(',', '')
			question = str(r["question"])
			question = question.replace(',', '')
			required = str(r["required"])
			result = str(r["result"])
			source = str(r["source"])
			breakdown = str(r["breakdown"]["total"]["Yea"])+"_"+str(r["breakdown"]["total"]["Nay"])+"_"+str(r["breakdown"]["total"]["Not Voting"])+"_"+str(r["breakdown"]["total"]["Present"])
			break_gop = str(r["breakdown"]["party"]["R"]["Yea"])+"_"+str(r["breakdown"]["party"]["R"]["Nay"])+"_"+str(r["breakdown"]["party"]["R"]["Not Voting"])+"_"+str(r["breakdown"]["party"]["R"]["Present"])
			break_dem = str(r["breakdown"]["party"]["D"]["Yea"])+"_"+str(r["breakdown"]["party"]["D"]["Nay"])+"_"+str(r["breakdown"]["party"]["D"]["Not Voting"])+"_"+str(r["breakdown"]["party"]["D"]["Present"])
			try:
				break_ind = str(r["breakdown"]["party"]["I"]["Yea"])+"_"+str(r["breakdown"]["party"]["I"]["Nay"])+"_"+str(r["breakdown"]["party"]["I"]["Not Voting"])+"_"+str(r["breakdown"]["party"]["I"]["Present"])
			except:
				break_ind = 'None'
			print voted_at
			if (datetime.strptime(voted_at, '%Y-%m-%dT%H:%M:%SZ') > topdate):
				entry = Votes(bill_id=bid,rid=rid,congress=congress,voted_at=voted_at,vote_type=vote_type,roll_type=roll_type,question=question,required=required,result=result,source=source,breakdown=breakdown,break_gop=break_gop,break_dem=break_dem,break_ind=break_ind)
				entry.put()
				#clog.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (bid,rid,congress,voted_at,vote_type,roll_type,question,required,result,source,breakdown,break_gop,break_dem,break_ind))
			else:
				breakvar = True
				break
		if (breakvar == True):
			break
		sleep(1.00)
