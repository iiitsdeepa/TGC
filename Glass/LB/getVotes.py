import urllib2
import json
from time import sleep
import datetime

#opening log file
congress = 114
clog_fname = 'votes' + str(congress) + '.csv'
clog = open(clog_fname, 'w')
clog_lname = 'ind_votes' + str(congress) + '.csv'
cilog = open(clog_lname, 'w')

chambers=['house','senate']
vote_url = 'https://congress.api.sunlightfoundation.com/votes?congress=%s&chamber=%s&per_page=50&%s&fields=voter_ids,bill_id,roll_id,congress,voted_at,vote_type,roll_type,question,required,result,source,breakdown&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
total_count = 0
for c in chambers:
	u = urllib2.urlopen(vote_url % (congress, c,'page=1'))
	b = u.read()
	j = json.loads(b)

	total_count += int(j["count"])
	per_page = int(j["page"]["per_page"])
	num_pages = int(j["count"])/per_page
	print j["count"],per_page,num_pages
	for x in range(1,num_pages+1):
		page = 'page='+str(x)
		u = urllib2.urlopen(vote_url % (congress, c, page))
		b = u.read()
		j = json.loads(b)
		ra = j["results"]
		print 'page '+str(x)
		for r in ra:
			try:
				bid = str(r["bill_id"])
			except:
				continue
			try:
				rid = str(r["roll_id"])
			except:
				rid = 'None'
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
				cilog.write('%s,%s,%s,%s\n' % (bid, rid, bioguide_id, vote))
			congress = str(r["congress"])
			voted_at = str(r["voted_at"])
			vote_type = str(r["vote_type"])
			roll_type = str(r["roll_type"])
			roll_type = roll_type.replace(',', '')
			question = str(r["question"])
			question = question.replace(',', '')
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
