#This file populates the Bill, BillKeyword, Keyword, Cosponsor tables. It also ads number of 

import urllib2
import json
import MySQLdb
from time import sleep

#connecting to the database
db = MySQLdb.connect(host="localhost", user="the_giver", passwd="memories", db="LegislativeBranch")
cursor = db.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

congress=110
billtype_convert = {'1':'hr', '2':'hres', '3':'hjres', '4':'hconres', '5':'s', '6':'sres', '7':'sjres', '8':'sconres'}
bill_url = 'https://congress.api.sunlightfoundation.com/bills?fields=bill_id,introduced_on,last_vote_at,official_title,popular_title,short_title,nicknames,keywords,summary_short,urls,enacted_as,sponsor_id,cosponsor_ids,cosponsor_count,keywords&%s&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'

def createBill(bill):
	bill_id = bill['bill_id'].encode('utf-8')
	official_title = bill['official_title'].encode('utf-8')
	try:
		short_title = bill['short_title'].encode('utf-8')
	except:
		short_title = 'none'
	try:
		popular_title = bill['popular_title'].encode('utf-8')
	except:
		popular_title = 'none'
	try:
		nickname = bill['nicknames'][0].encode('utf-8')
	except:
		nickname = 'none'
	try:
		summary_short = bill['summary_short'].encode('utf-8')
	except:
		summary_short = 'none'
	try:
		link = bill['urls']['congress'].encode('utf-8')
	except:
		link = 'none'
	try:
		sponsor_id = bill['sponsor_id'].encode('utf-8')
	except:
		sponsor_id = 'none'


k=1
total_bills = 0
#loop through each of the bill types
while k <= 8:
	bill_type = billtype_convert['%s' %k]
	print bill_type
	bill_method = 'congress=%d&bill_type=%s&per_page=50' % (congress, bill_type)
	ubills = urllib2.urlopen(bill_url % bill_method)
	bills = ubills.read()
	jbills = json.loads(bills)
	total_bills += jbills['count']
	per_page = 50
	num_pages = (total_bills / per_page) + 2

	print 'WORKING ON %s, NUM_PAGES = %s' % (bill_type, num_pages)
	#loop through each page received from api
	i = 0
	while i < num_pages: #num_pages
		bill_method = 'congress=%d&bill_type=%s&per_page=50&page=%d' % (congress, bill_type, i)
		ubills = urllib2.urlopen(bill_url % bill_method)
		bills = ubills.read()
		jbills = json.loads(bills)
		print 'STARTING PAGE %d' % i

		#loop through each bill, populating all tables associated
		bills = jbills['results']

		i+=1

	print total_bills, num_pages
	if k == 4:
		totalhbills = total_bills
		total_bills = 0
	elif k == 8:
		totalsbills = total_bills
	k += 1

print totalhbills, totalsbills