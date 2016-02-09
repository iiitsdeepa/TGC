# import os
# import re
# import random
# import hashlib
# import hmac
# import urllib2
# import json
# import pdb
# import logging
# import random, string
# from string import letters
# import csv
# import datetime

# import webapp2
# import jinja2
# import cgi
# from time import sleep
# from google.appengine.ext.webapp.util import run_wsgi_app
# from datetime import datetime, date, time

# from google.appengine.ext import db
# from google.appengine.ext import blobstore
# from google.appengine.ext.webapp import blobstore_handlers
# from google.appengine.ext.db import GqlQuery
# from google.appengine.api import mail
# import politics
# from databaseclasses import *
# from csvprocessing import *

# def getCosponsorsUpdate():
# 	congress = 114
# 	chambers=['hr','s']
# 	bill_url = 'https://congress.api.sunlightfoundation.com/bills?%s&fields=bill_id,cosponsor_ids&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
# 	total_count = 0
# 	for c in chambers:
# 		bill_method = 'congress=%d&bill_type=%s&per_page=20&page=%d' % (congress,c, 1)
# 		u = urllib2.urlopen(bill_url % bill_method)
# 		b = u.read()
# 		j = json.loads(b)
# 		total_count += int(j["count"])
# 		per_page = int(j["page"]["per_page"])
# 		num_pages = int(j["count"])/per_page
# 		logging.error(str(total_count)+" "+str(per_page)+" "+str(num_pages))
# 		breakvar = False
# 		breakcount = 1
# 		for x in range(1,num_pages+1):
# 			bill_method = 'congress=%d&bill_type=%s&per_page=20&page=%d' % (congress,c, x)
# 			u = urllib2.urlopen(bill_url % bill_method)
# 			b = u.read()
# 			j = json.loads(b)
# 			ra = j["results"]
# 			logging.error('page '+str(j["page"]["page"]))
# 			for r in ra:
# 				try:
# 					bid = r["bill_id"].encode('utf-8')
# 				except:
# 					bid = 'None'
# 				#parse for cosponsors
# 				logging.error(bid)
# 				try:
# 					cosponsorsa = r["cosponsor_ids"]
# 					entry = []
# 					for tempco in iter(cosponsorsa):
# 						line = tempco.encode('utf-8')
# 						bioidquery = GqlQuery("SELECT * FROM Cosponsor WHERE bill_id = :1 AND bioguide_id = :2", bid, line)
# 						tempqueryrow = bioidquery.get()
# 						if tempqueryrow is None:
# 							logging.error('IF')
# 							entry.append(Cosponsor(bill_id=bid,bioguide_id=line))
# 						elif (breakcount == 1):
# 							logging.error('ELIF BREAKCOUNT')
# 							breakcount = breakcount - 1
# 						else:
# 							logging.error('ELSE')
# 					db.put(entry)
# 				except:
# 					continue
# 			if (breakvar == True):
# 				break
# 			if (breakcount == 0):
# 				breakvar = True
# 			sleep(1.00)