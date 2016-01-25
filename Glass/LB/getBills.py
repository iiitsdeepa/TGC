import urllib2
import json
from datetime import datetime
from time import sleep

#opening log file
congress = 114
billscsv = open('bills'+str(congress)+'.csv', 'w')
cosponsorscsv = open('cosponsors'+str(congress)+'.csv', 'w')
keywordscsv = open('keywords'+str(congress)+'.csv', 'w')

chambers=['hr','s']
bill_url = 'https://congress.api.sunlightfoundation.com/bills?%s&fields=bill_id,official_title,popular_title,short_title,nicknames,urls,active,vetoed,enacted,sponsor_id,introduced_on,history,last_action_at&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
total_count = 0
for c in chambers:
	bill_method = 'congress=%d&bill_type=%s&per_page=20&page=%d' % (congress,c, 1)
	u = urllib2.urlopen(bill_url % bill_method)
	b = u.read()
	j = json.loads(b)
	ch = c
	total_count += int(j["count"])
	per_page = int(j["page"]["per_page"])
	num_pages = int(j["count"])/per_page
	print total_count,per_page,num_pages
	for x in range(1,num_pages+1):
		bill_method = 'congress=%d&bill_type=%s&per_page=20&page=%d' % (congress,ch, x)
		u = urllib2.urlopen(bill_url % bill_method)
		b = u.read()
		j = json.loads(b)
		#print json.dumps(j, indent=4)
		ra = j["results"]
		print 'page '+str(x)
		for r in ra:
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
			last_action = r["last_action_at"]
			introduced = r["introduced_on"]
		   	#parse for cosponsorscsv and keyowrdscsv
		   	try:
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
		   	line = bid+'$$$'+official_title+'$$$'+popular_title+'$$$'+short_title+'$$$'+nicknames+'$$$'+url+'$$$'+active+'$$$'+vetoed+'$$$'+enacted+'$$$'+introduced+'$$$'+last_action+'\n'
			billscsv.write(line)
		sleep(1.00)


print total_count

billscsv.close()
cosponsorscsv.close()
keywordscsv.close()
