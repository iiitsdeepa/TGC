import urllib2
import json
from time import sleep

#opening log file
csv = open('bills112.csv', 'w')

congress = 112
chambers=['house','senate']
bill_url = 'https://congress.api.sunlightfoundation.com/bills?congress=%s&chamber=%s&per_page=50&%s&fields=bill_id,official_title,popular_title,short_title,nicknames,keywords,summary_short,urls,history.active,history.vetoed,history.vetoed_at,history.enacted,history.enacted_at,sponsor_id,cosponsor_ids,cosponsor_count,keywords&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
total_count = 0
for c in chambers:
	u = urllib2.urlopen(bill_url % (congress, c,'page=1'))
	b = u.read()
	j = json.loads(b)

	total_count += int(j["count"])
	per_page = int(j["page"]["per_page"])
	num_pages = int(j["count"])/per_page
	print total_count,per_page,num_pages
	for x in range(1,num_pages+1):
		page = 'page='+str(x)
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
				rid = r["roll_id"].encode('utf-8')
			except:
				rid = '-1'
			"""try:
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
		   	try:
				keywordsa = r["keywords"].encode('utf-8')
				keywords = '$$$'.join(keywordsa)
				#keywords = "$$$".join(keywords)
			except:
		   		keywords = 'None'
		   	"""
		    
		   	line = bid+','+rid+','+'\n'
			csv.write(line)
		sleep(1.00)


print total_count

#"bill_id": "hr41-113", (link to Bills table)
#"roll_id": "h7-2013",
#"congress": 113,
#"voted_at": "2013-01-04T16:22:00Z", (date-time type)
#"vote_type": "passage",
#"roll_type": "On Motion to Suspend the Rules and Pass",
#"question": "On Motion to Suspend the Rules and Pass -- H.R. 41 -- To temporarily increase the borrowing authority of the Federal Emergency Management Agency for carrying out the National Flood Insurance Program",
#"required": "2/3",
#"result": "Passed",
#"source": "http://clerk.house.gov/evs/2013/roll007.xml"
#“breakdown”: [yea_nay_pres_not]
#“break_gop”:[yea_nay_pres_not]
#“break_dem”:[yea_nay_pres_not]
#“break_ind”:[yea_nay_pres_not]

#second table: Ind_Votes
#bill_id
#bioguide_id (voter)
#vote: (Y,N,P,NV,O) votes are either yea, nay, present, not voting, or other
