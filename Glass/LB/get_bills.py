import urllib2
import json
from time import sleep

#opening log file
csv = open('bills.csv', 'w')

congress = 112
chambers=['hr','s']
bill_url = 'https://congress.api.sunlightfoundation.com/bills?fields=bill_id,official_title,popular_title,short_title,nicknames,keywords,summary_short,urls,history.active,history.vetoed,history.vetoed_at,history.enacted,history.enacted_at,sponsor_id,cosponsor_ids,cosponsor_count,keywords&congress=%s&bill_type=%s&per_page=50&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
for c in chambers
	u = urllib2.urlopen(bill_url % (congress, 's'))
	b = u.read()
	j = json.loads(b)

	total_count = j["count"]
	ra = j["results"]
	for r in ra:
		bid = r["bill_id"]
		official_title = r["official_title"]
		popular_title = r["popular_title"]
		short_title = r["short_title"]
		try:
			nicknamesa = r["nicknames"]
			nicknames = '$$$'.join(nicknamesa)
		except:
	   		nicknames = 'null'
	   	try:
			keywordsa = r["keywords"]
			keywords = '$$$'.join(keywordsa)
			#keywords = "$$$".join(keywords)
		except:
	   		keywords = 'null'
	   	url = r["urls"]["congress"]
	   	active = r["history"]["active"]
	   	vetoed = r["history"]["vetoed"]
	   	enacted = r["history"]["enacted"]
	   	sponsor = r["sponsor_id"]
	   	try:
			cosponsorsa = r["cosponsor_ids"]
			cosponsors = '$$$'.join(cosponsorsa)
		except:
	   		cosponsors = 'null'


	   	print bid,official_title,popular_title,short_title,url,active,vetoed,enacted,sponsor,cosponsors



csv.write(json.dumps(j,indent=4))
