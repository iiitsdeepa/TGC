import os
import re
import random
import hashlib
import hmac
import urllib2
import json
import pdb
import logging
import random, string
from string import letters
import csv
import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import webapp2
import jinja2
import cgi
from time import sleep
from google.appengine.ext.webapp.util import run_wsgi_app
from datetime import datetime, date, time

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.db import GqlQuery
from google.appengine.api import mail
import politics

def getBillsUpdate():
	bill_url = 'https://congress.api.sunlightfoundation.com/bills?%s&fields=bill_id,official_title,popular_title,short_title,nicknames,urls,active,vetoed,enacted,sponsor_id,introduced_on,history,last_action_at&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
	tempdate = GqlQuery("SELECT last_action FROM Bill ORDER BY last_action DESC").get()
	try:
		topdate = tempdate.last_action
	except:
		topdate = datetime.min
	congress = 114
	chambers=['hr','s']
	total_count = 0
	for c in chambers:
		bill_method = 'congress=%d&bill_type=%s&per_page=20&page=%d' % (congress,c, 1)
		u = urllib2.urlopen(bill_url % bill_method)
		b = u.read()
		j = json.loads(b)
		total_count += int(j["count"])
		per_page = int(j["page"]["per_page"])
		num_pages = int(j["count"])/per_page
		logging.error(str(c)+" "+str(total_count)+" "+str(per_page)+" "+str(num_pages))
		breakvar = False
		for x in range(1,num_pages+1):
			bill_method = 'congress=%d&bill_type=%s&per_page=20&page=%d' % (congress,c, x)
			u = urllib2.urlopen(bill_url % bill_method)
			b = u.read()
			j = json.loads(b)
			ra = j["results"]
			logging.error('page '+str(x))
			for r in ra:
				try:
					last_action = datetime.strptime(r["last_action_at"], '%Y-%m-%d')
				except:
					last_action = datetime.strptime(r["last_action_at"], '%Y-%m-%dT%H:%M:%SZ')
				if (last_action <= topdate):
					breakvar = True
					break
				try:
					bid = r["bill_id"].encode('utf-8')
				except:
					bid = 'None'
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
				try:
					introduced = datetime.strptime(r["introduced_on"], '%Y-%m-%d')
				except:
					introduced = datetime.strptime(r["introduced_on"], '%Y-%m-%dT%H:%M:%SZ')

				repeat = GqlQuery("SELECT Key, last_action FROM Bill WHERE bill_id = :1", bid).get()
				try:
					logging.error(str(repeat.key))
					repeatbill = repeat.last_action
					if (repeatbill < last_action):
						todelete = db.Key.from_path('Bill', str(repeat.Key))
						db.delete(todelete)
				except:
					repeatbill = 0
				entry = politics.Bill(bill_id=bid,official_title=official_title,popular_title=popular_title,short_title=short_title,nicknames=nicknames,url=url,active=active,vetoed=vetoed,enacted=enacted,sponsor_id=sponsor, introduced=introduced, last_action=last_action, last_updated=datetime.today())
				#entry.put()
			sleep(1.00)
			if (breakvar == True):
				break
