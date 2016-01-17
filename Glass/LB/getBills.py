import urllib2
import json
from time import sleep

#opening log file
congress = 114
billscsv = open('bills'+str(congress)+'.csv', 'w')
cosponsorscsv = open('cosponsors'+str(congress)+'.csv', 'w')
keywordscsv = open('keywords'+str(congress)+'.csv', 'w')

chambers=['hr','s']
bill_url = 'https://congress.api.sunlightfoundation.com/bills?fields=bill_id,official_title,popular_title,short_title,nicknames,keywords,summary_short,urls,history.active,history.vetoed,history.vetoed_at,history.enacted,history.enacted_at,sponsor_id,cosponsor_ids,cosponsor_count,keywords&congress=%s&bill_type=%s&per_page=50&%sapikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
total_count = 0
for c in chambers:
	u = urllib2.urlopen(bill_url % (congress, c,'page=1&'))
	b = u.read()
	j = json.loads(b)

	total_count += int(j["count"])
	per_page = int(j["page"]["per_page"])
	num_pages = int(j["count"])/per_page
	print total_count,per_page,num_pages
	for x in range(1,num_pages+1):
		page = 'page='+str(x)+'&'
		u = urllib2.urlopen(bill_url % (congress, c, page))
		b = u.read()
		j = json.loads(b)
		ra = j["results"]
		print 'page '+str(x)
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
		   	line = bid+','+official_title+','+popular_title+','+short_title+','+nicknames+','+url+','+active+','+vetoed+','+enacted+','+sponsor+'\n'
			billscsv.write(line)
		sleep(1.00)


print total_count

billscsv.close()
cosponsorscsv.close()
keywordscsv.close()
