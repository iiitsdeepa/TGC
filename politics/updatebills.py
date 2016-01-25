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
from databaseclasses import *

"""
The point behind this method is to pull the latest bills data from the sunlight foundation, adding them to the Bill table in the database.
If the updater encounters a bill that already exists in the table, it will remove the old bill data from the table.
It then replaces the deleted bill with a new one with the accurate information. 
If no duplicate exists then the bill is just put into the table directly.

The method stops when it encounters bills that have the same last_action_at date as ones that already exist in the table.
This keeps the method from overwriting the entire Bill table each time it is ran.
If the Bill table is empty before this method is run, the default time to compare to is set to datetime.min, which is approx equal to Jan 1, 1900; 00:00:00
"""
def getBillsUpdate():
	#some initializating of necesary queries and variables
	bill_url = 'https://congress.api.sunlightfoundation.com/bills?%s&fields=bill_id,official_title,popular_title,short_title,nicknames,urls,active,vetoed,enacted,sponsor_id,introduced_on,history,last_action_at&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
	tempdate = GqlQuery("SELECT last_action FROM Bill ORDER BY last_action DESC").get()
	try:#pulls the last_action_at date from the Bill table. If that fails, topdate is set to datetime.min
		topdate = tempdate.last_action
		logging.error('topdate')
	except:
		logging.error('datetime.min')
		topdate = datetime.min
	congress = 114
	chambers=['hr','s']
	total_count = 0
	#this for loop goes through each chamber of congress and pulls their respective bills
	for c in chambers:
		bill_method = 'congress=%d&bill_type=%s&per_page=20&page=%d' % (congress,c, 1)
		u = urllib2.urlopen(bill_url % bill_method)
		b = u.read()
		j = json.loads(b)
		#integers to count how many pages the code needs to process through to reach them all
		total_count += int(j["count"])
		per_page = int(j["page"]["per_page"])
		num_pages = int(j["count"])/per_page
		logging.error(str(c)+" "+str(total_count)+" "+str(per_page)+" "+str(num_pages))
		breakvar = False
		#this for loop goes through each page in the api database, starting at page = 1 (most recent) and going to the end (earliest)
		for x in range(1,num_pages+1):
			bill_method = 'congress=%d&bill_type=%s&per_page=20&page=%d' % (congress,c, x)
			u = urllib2.urlopen(bill_url % bill_method)
			b = u.read()
			j = json.loads(b)
			ra = j["results"]
			logging.error('page '+str(x))
			#this for loop jumps through each entry in the results list (ra). The api is currently set to pull 20 results per page
			for r in ra:
				try:
					last_action = datetime.strptime(r["last_action_at"], '%Y-%m-%d')
				except:
					last_action = datetime.strptime(r["last_action_at"], '%Y-%m-%dT%H:%M:%SZ')
				#this if statement determines if the current result's last_action_at is the same or lower than the latest last_action_at in the database.
				#if this is true, that means that we don't need to update the table anymore and can break out of the loop.
				if (last_action <= topdate):
					breakvar = True
					break
				#the following statements encode the results to 'utf-8'/strings to allow them to be put into the Bill table
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
				#this last try-except statement tests to see if the bill_id already exists in the table.
				#if true the older existing bill will be deleted
				try:
					repeatedbill = Bill.gql("WHERE bill_id = :1", str(bid)).get()
					repeatedbill.delete()
				except:
					repeatbill = 0
				#place the bill entity into the Bill table
				entry = Bill(bill_id=bid,official_title=official_title,popular_title=popular_title,short_title=short_title,nicknames=nicknames,url=url,active=active,vetoed=vetoed,enacted=enacted,sponsor_id=sponsor, introduced=introduced, last_action=last_action, last_updated=datetime.today())
				entry.put()
			sleep(1.00)#always sleep for 1 second to be a nice citizen to the sunlight api and not DOS their servers :)
			if (breakvar == True):
				break
