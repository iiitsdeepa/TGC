import urllib2
import json
from time import sleep
import datetime

#opening log file
congress = 114
clog_fname = str(congress) + 'Votes.csv'
clog = open(clog_fname, 'w')
clog_lname = str(congress) + 'Ind_Votes.csv'
cilog = open(clog_lname, 'w')

chambers=['house','senate']
bill_url = 'https://congress.api.sunlightfoundation.com/votes?congress=%s&chamber=%s&per_page=50&%s&fields=voter_ids,bill_id,roll_id,congress,voted_at,vote_type,roll_type,question,required,result,source,breakdown&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
total_count = 0
for c in chambers:
	u = urllib2.urlopen(bill_url % (congress, c,'page=1'))
	b = u.read()
	j = json.loads(b)

	total_count += int(j["count"])
	per_page = int(j["page"]["per_page"])
	num_pages = int(j["count"])/per_page
	print j["count"],per_page,num_pages
	for x in range(1,num_pages+1):
		page = 'page='+str(x)
		u = urllib2.urlopen(bill_url % (congress, c, page))
		b = u.read()
		j = json.loads(b)
		ra = j["results"]
		print 'page '+str(x)
		for r in ra:
			try:
				bid = str(r["bill_id"])
			except:
				continue
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
				cilog.write('%s,%s,%s\n' % (bid, bioguide_id, vote))
			try:
				rid = str(r["roll_id"])
			except:
				rid = 'None'
			congress = str(r["congress"])
			voted_at = str(r["voted_at"])
			vote_type = str(r["vote_type"])
			roll_type = str(r["roll_type"])
			question = str(r["question"])
			required = str(r["required"])
			result = str(r["result"])
			source = str(r["source"])
			breakdown = str(r["breakdown"]["total"]["Yea"])+"_"+str(r["breakdown"]["total"]["Nay"])+"_"+str(r["breakdown"]["total"]["Not Voting"])+"_"+str(r["breakdown"]["total"]["Present"])
			break_gop = str(r["breakdown"]["party"]["R"]["Yea"])+"_"+str(r["breakdown"]["party"]["R"]["Nay"])+"_"+str(r["breakdown"]["party"]["R"]["Not Voting"])+"_"+str(r["breakdown"]["party"]["R"]["Present"])
			break_dem = str(r["breakdown"]["party"]["D"]["Yea"])+"_"+str(r["breakdown"]["party"]["D"]["Nay"])+"_"+str(r["breakdown"]["party"]["D"]["Not Voting"])+"_"+str(r["breakdown"]["party"]["D"]["Present"])
			try:
				break_ind = str(r["breakdown"]["party"]["I"]["Yea"])+"_"+str(r["breakdown"]["party"]["I"]["Nay"])+"_"+str(r["breakdown"]["party"]["I"]["Not Voting"])+"_"+str(r["breakdown"]["party"]["I"]["Present"])
			except:
				break_ind = 'None'
			clog.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (bid,rid,congress,voted_at,vote_type,roll_type,question,required,result,source,breakdown,break_gop,break_dem,break_ind))
		sleep(1.00)


print total_count
clog.close()
cilog.close()

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
