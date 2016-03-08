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
						average = [0,0,0,0,0]
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
						average[4] = float(average[4])/float(count)
					for each in average:
						t = dict(v=each)
						retarray.append(t)
					ret = dict(c=retarray)
					if i == 0:
						rows.append(ret)
					else:
						rows.insert(0,ret)
				keytext = str(p)+ str(smooth) + str(time)
				memcache.add(keytext, rows, 86400)
				if returnvar:
					return rows