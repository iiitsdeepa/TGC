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
from indvoteupdate import *
from databaseclasses import *

"""
This method updates the Votes table with the latest information from the sunlight foundation adding them to the Votes table in the database.
At the end of this method, the indVoteUpdate method is called to update the Ind_Votes table
The method stops when it encounters votess that have the same last_action_at date as ones that already exist in the table.
This keeps the method from overwriting the entire Votes table each time it is ran.
If the Votes table is empty before this method is run, the default time to compare to is set to datetime.min, which is approx equal to Jan 1, 1900; 00:00:00
"""

def getVotesUpdate():
	#some initializating of necesary queries and variables
	congress = 114
	tempdate = GqlQuery("SELECT voted_at FROM Votes ORDER BY voted_at DESC").get()
	try:#pulls the last_action_at date from the Votes table. If that fails, topdate is set to datetime.min
		topdate = datetime.strptime(tempdate.voted_at, '%Y-%m-%dT%H:%M:%SZ')
	except:
		topdate = datetime.min

	chambers=['house','senate']
	bill_url = 'https://congress.api.sunlightfoundation.com/votes?congress=%s&chamber=%s&per_page=10&%s&fields=voter_ids,bill_id,roll_id,congress,voted_at,vote_type,roll_type,question,required,result,source,breakdown&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
	total_count = 0
	voteinput = []
	vcount = 0
	#this for loop goes through each chamber of congress and pulls their respective votes
	for c in chambers:
		u = urllib2.urlopen(bill_url % (congress, c,'page=1'))
		b = u.read()
		j = json.loads(b)
		#integers to count how many pages the code needs to process through to reach them all
		total_count += int(j["count"])
		per_page = int(j["page"]["per_page"])
		num_pages = int(j["count"])/per_page
		breakvar = False
		logging.error(str(total_count)+" "+str(num_pages))
		#this for loop goes through each page in the api database, starting at page = 1 (most recent) and going to the end (earliest)
		for x in range(1,num_pages+1):
			page = 'page='+str(x)
			logging.error(str(page))
			u = urllib2.urlopen(bill_url % (congress, c, page))
			b = u.read()
			j = json.loads(b)
			ra = j["results"]
			#this for loop jumps through each entry in the results list (ra). The api is currently set to pull 20 results per page
			for r in ra:
				voted_at = str(r["voted_at"])
				#this if statement determines if the current result's voted_at is the same or lower than the latest votes_at in the database.
				#if this is true, that means that we don't need to update the table anymore and can break out of the loop.
				if (datetime.strptime(voted_at, '%Y-%m-%dT%H:%M:%SZ') <= topdate):
					breakvar = True
					break
				#the following statements encode the results to 'utf-8'/strings to allow them to be put into the Votes table
				try:
					bid = str(r["bill_id"])
				except:
					continue
				try:
					rid = str(r["roll_id"])
				except:
					rid = 'None'
				#this for loop creates a list of individual voter_ids and how they vote. 
				#This list will be passed onto the indvotesupdate method to update the Ind_Votes table
				for bioguide_id, vote in r['voter_ids'].items():
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
					voteinput.append([bid, rid, bioguide_id, vote])
					vcount += 1
				congress = str(r["congress"])
				vote_type = str(r["vote_type"])
				roll_type = str(r["roll_type"])
				roll_type = roll_type.replace(',', '')#some roll_types have commas built in, this was used to delete them for the csv file
				question = str(r["question"])
				question = question.replace(',', '')
				required = str(r["required"])
				result = str(r["result"])
				source = str(r["source"])
				#party breakdowns are arranged in the following order: Yea_Nay_Not Voting_Present
				breakdown = str(r["breakdown"]["total"]["Yea"])+"_"+str(r["breakdown"]["total"]["Nay"])+"_"+str(r["breakdown"]["total"]["Not Voting"])+"_"+str(r["breakdown"]["total"]["Present"])
				break_gop = str(r["breakdown"]["party"]["R"]["Yea"])+"_"+str(r["breakdown"]["party"]["R"]["Nay"])+"_"+str(r["breakdown"]["party"]["R"]["Not Voting"])+"_"+str(r["breakdown"]["party"]["R"]["Present"])
				break_dem = str(r["breakdown"]["party"]["D"]["Yea"])+"_"+str(r["breakdown"]["party"]["D"]["Nay"])+"_"+str(r["breakdown"]["party"]["D"]["Not Voting"])+"_"+str(r["breakdown"]["party"]["D"]["Present"])
				try:
					break_ind = str(r["breakdown"]["party"]["I"]["Yea"])+"_"+str(r["breakdown"]["party"]["I"]["Nay"])+"_"+str(r["breakdown"]["party"]["I"]["Not Voting"])+"_"+str(r["breakdown"]["party"]["I"]["Present"])
				except:
					break_ind = 'None'
				#place the votes entity into the Votes table
				entry = Votes(bill_id=bid,rid=rid,congress=congress,voted_at=voted_at,vote_type=vote_type,roll_type=roll_type,question=question,required=required,result=result,source=source,breakdown=breakdown,break_gop=break_gop,break_dem=break_dem,break_ind=break_ind)
				entry.put()
			if (breakvar == True):
				break
			sleep(1.00)#always sleep for 1 second to be a nice citizen to the sunlight api and not DOS their servers :)
	#indVoteUpdate(voteinput)