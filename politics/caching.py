from basehandler import *
from datetime import datetime, date, time, timedelta
import databaseclasses
from google.appengine.api import memcache

def updateCache():
	setNatPolls(0, 0, '', '')

def setNatPolls(l, s, inparty, incolor):
	if l == 0 and s == 0 and inparty == '' and incolor == '':
		times = [30, 60, 120, 180, 360]
		smoothings = [10, 20, 30, 45, 90]
		party = ['dnpolls', 'rnpolls']
		colorthing = ['hill$$$sanders','trump$$$cruz$$$rubio$$$kasich']
		colorcount = 0
		returnvar = False
	else:
		times = [l]
		smoothings = [s]
		party = [inparty]
		colorthing = incolor
		returnvar = True
		colorcount = -1
	for p in party:
		if colorcount == -1:
			tempcolor = colorthing
		else:
			tempcolor = colorthing[colorcount]
			colorcount += 1
		for time in times:
			for sm in smoothings:
				rows = []
				length = time
				smooth = sm
				ultstartday = datetime.now() - timedelta(days=(int(smooth)+int(length)))
				ultendday = datetime.now()
				if p == 'dnpolls':
					querystr = 'SELECT * FROM NationalDemocraticPrimary WHERE entry_date >= :1 AND entry_date <= :2'
				else:
					querystr = 'SELECT * FROM NationalRepublicanPrimary WHERE entry_date >= :1 AND entry_date <= :2'
				query = GqlQuery(querystr, ultstartday, ultendday)
				masterquery = []
				for row in query:
					masterquery.append(row)
				for i in range(int(length)):
					startday = datetime.now() - timedelta(days=(i+int(smooth)))
					endday = datetime.now() - timedelta(days=i)
					tempquery = []
					for mq in masterquery:
						if mq.entry_date >= startday and mq.entry_date <= endday:
							tempquery.append(mq)
					endday = endday.date()
					retarray = [{"v":str(endday)}]
					if p == 'dnpolls':
						average = [0,0]
					else:
						average = [0,0,0,0]
					count = 0
					for each in tempquery:
						narray = tempcolor.split('$$$')
						for i in range(len(narray)):
							temp = getattr(each,narray[i])
							average[i] += temp
						count += 1
					for j in range(len(average)):
						if average[j] < 0:
							average[j] = 0;
					if p == 'dnpolls' and count != 0:
						average[0] = float(average[0])/float(count)
						average[1] = float(average[1])/float(count)
					elif count != 0:
						average[0] = float(average[0])/float(count)
						average[1] = float(average[1])/float(count)
						average[2] = float(average[2])/float(count)
						average[3] = float(average[3])/float(count)
					for each in average:
						t = dict(v=each)
						retarray.append(t)
					ret = dict(c=retarray)
					if i == 0:
						rows.append(ret)
					else:
						rows.insert(0,ret)
				for i in range(int(length)):
					for j in range(len(rows[i]['c'])-1):
						if i > 0 and rows[i]['c'][j+1]['v'] == 0:
							rows[i]['c'][j+1]['v'] = rows[i-1]['c'][j+1]['v']
				keytext = str(p)+ str(smooth) + str(time)
				memcache.add(keytext, rows, 86400)
				if returnvar:
					return rows

def codeToName(code):
	statedict = {'al':'alabama',
				 'ak':'alaska',
				 'az':'arizona',
				 'ar':'arkansas',
				 'ca':'california',
				 'co':'colorado',
				 'ct':'connecticut',
				 'de':'deleware',
				 'fl':'florida',
				 'ga':'georgia',
				 'hi':'hawaii',
				 'id':'idaho',
				 'il':'illinois',
				 'in':'indiana',
				 'ia':'iowa',
				 'ks':'kansas',
				 'ky':'kentucky',
				 'la':'louisiana',
				 'me':'maine',
				 'md':'maryland',
				 'ma':'massachusetts',
				 'mi':'michigan',
				 'mn':'minnesota',
				 'ms':'mississippi',
				 'mo':'missouri',
				 'mt':'montana',
				 'ne':'nebraska',
				 'nv':'nevada',
				 'nh':'new-hampshire',
				 'nj':'new-jersey',
				 'nm':'new-mexico',
				 'ny':'new-york',
				 'nc':'north-carolina',
				 'nd':'north-dakota',
				 'oh':'ohio',
				 'ok':'oklahoma',
				 'or':'oregon',
				 'pa':'pennsylvania',
				 'ri':'rhode-island',
				 'sc':'south-carolina',
				 'sd':'south-dakota',
				 'tn':'tennessee',
				 'tx':'texas',
				 'ut':'utah',
				 'vt':'vermont',
				 'va':'virginia',
				 'wa':'washington',
				 'wv':'west-virginia',
				 'wi':'wisconsin',
				 'wy':'wyoming'}
	return statedict[code]

def setStatePolls(pollname, polcolor):
	pollname = pollname[4:]
	party = pollname[0:1]
	statename = codeToName(pollname[1:3])
	tempcolor = polcolor
	rows = []
	smooth = 10
	length = 90
	ultstartday = datetime.now() - timedelta(days=(int(smooth)+int(length)))
	ultendday = datetime.now()
	if party == 'd':
		querystr = 'SELECT * FROM StateDemocraticPrimary WHERE entry_date >= :1 AND entry_date <= :2 AND state = :3'
	else:
		querystr = 'SELECT * FROM StateRepublicanPrimary WHERE entry_date >= :1 AND entry_date <= :2 AND state = :3'
	query = GqlQuery(querystr, ultstartday, ultendday, statename)
	masterquery = []
	for row in query:
		masterquery.append(row)
	for i in range(int(length)):
		startday = datetime.now() - timedelta(days=(i+int(smooth)))
		endday = datetime.now() - timedelta(days=i)
		tempquery = []
		for mq in masterquery:
			if mq.entry_date >= startday and mq.entry_date <= endday:
				tempquery.append(mq)
		endday = endday.date()
		retarray = [{"v":str(endday)}]
		if party == 'd':
			average = [0,0]
		else:
			average = [0,0,0,0]
		count = 0
		for each in tempquery:
			narray = tempcolor.split('$$$')
			for i in range(len(narray)):
				temp = getattr(each,narray[i])
				average[i] += temp
			count += 1
		for j in range(len(average)):
			if average[j] < 0:
				average[j] = 0;
		if party == 'd' and count != 0:
			average[0] = float(average[0])/float(count)
			average[1] = float(average[1])/float(count)
		elif count != 0:
			average[0] = float(average[0])/float(count)
			average[1] = float(average[1])/float(count)
			average[2] = float(average[2])/float(count)
			average[3] = float(average[3])/float(count)
		for each in average:
			t = dict(v=each)
			retarray.append(t)
		ret = dict(c=retarray)
		if i == 0:
			rows.append(ret)
		else:
			rows.insert(0,ret)
	for i in range(length):
		for j in range(len(rows[i]['c'])-1):
			if i > 0 and rows[i]['c'][j+1]['v'] == 0:
				rows[i]['c'][j+1]['v'] = rows[i-1]['c'][j+1]['v']
	keytext = pollname
	logging.error(rows)
	memcache.add(keytext, rows, 86400)
	return rows