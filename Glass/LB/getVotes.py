import urllib2
import json
from time import sleep
import datetime

#opening log file
congress = 112
clog_fname = str(congress) + 'Votes.csv'
csv = open(clog_fname, 'w')

chambers=['house','senate']
bill_url = 'https://congress.api.sunlightfoundation.com/votes?congress=%s&chamber=%s&per_page=50&%s&fields=bill_id,roll_id,congress,voted_at,vote_type,roll_type,question,required,result,source,breakdown&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
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
			congress = r["congress"]
			voted_at = r["voted_at"]
			vote_type = r["vote_type"]
			roll_type = r["roll_type"]
			question = r["question"]
			required = r["required"]
			result = r["result"]
			source = r["source"]
			breakdown = str(r["breakdown"]["total"]["Yea"])+"_"+str(r["breakdown"]["total"]["Nay"])+"_"+str(r["breakdown"]["total"]["Not Voting"])+"_"+str(r["breakdown"]["total"]["Present"])
			break_gop = str(r["breakdown"]["R"]["Yea"])+"_"+str(r["breakdown"]["R"]["Nay"])+"_"+str(r["breakdown"]["R"]["Not Voting"])+"_"+str(r["breakdown"]["R"]["Present"])
			break_dem = str(r["breakdown"]["D"]["Yea"])+"_"+str(r["breakdown"]["D"]["Nay"])+"_"+str(r["breakdown"]["D"]["Not Voting"])+"_"+str(r["breakdown"]["D"]["Present"])
			break_ind = str(r["breakdown"]["I"]["Yea"])+"_"+str(r["breakdown"]["I"]["Nay"])+"_"+str(r["breakdown"]["I"]["Not Voting"])+"_"+str(r["breakdown"]["I"]["Present"])
			line = bid+','+rid+','+congress+','+voted_at+','+vote_type+','+roll_type+','+question+','+required+','+result+','+source+','+breakdown+','+break_gop+','+break_dem+','+break_ind+'\n'
			csv.write(line)
		sleep(1.00)


print total_count
bill_id,roll_id,congress,voted_at,vote_type,roll_type,question,required,result,source,breakdown

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
#'breakdown': [yea_nay_pres_not]
#'break_gop':[yea_nay_pres_not]
#'break_dem':[yea_nay_pres_not]
#'break_ind':[yea_nay_pres_not]

#second table: Ind_Votes
#bill_id
#bioguide_id (voter)
#vote: (Y,N,P,NV,O) votes are either yea, nay, present, not voting, or other
