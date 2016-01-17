import urllib2
import json
from time import sleep

namelist = open('113namelist.csv', 'r')

def getCongress(cnum):
	clog_fname = str(cnum) + '_bid_member.csv'
	clog = open(clog_fname, 'w')
	errlog = open('113errlog.txt', 'w')
	url = 'https://congress.api.sunlightfoundation.com/legislators?all_legislators=true&last_name=%s&first_name=%s&state=%s&fields=bioguide_id,govtrack_id,crp_id,first_name,last_name,gender,birthday,terms.start,terms.end,state,district,state_rank,chamber,party,twitter_id,facebook_id,phone,website,contact_form,fax&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
	namelist = str(cnum) + 'namelist.csv'
	nl = open(namelist)
	num_pols = 0
	senswitch = 0
	for l in iter(nl):
		#print str(l)
		errlog.write('%s' % l)
		if (str(l) == "SENATORS\n"):
			senswitch = 1
		elif (senswitch == 1):
			st,fn1,ln1,andent,fn2,ln2 = l.split(',')
			ln2 = ln2[:-1]
			upols1 = urllib2.urlopen(url % (ln1,fn1,st))
			pols1 = upols1.read()
			jpols1 = json.loads(pols1)
			sleep(1.00)
			upols2 = urllib2.urlopen(url % (ln2,fn2,st))
			pols2 = upols2.read()
			jpols2 = json.loads(pols2)
			if jpols1['count'] != 1:
				print (fn1, ln1, jpols1['count'])
			else:
				p1 = jpols1['results'][0]
				clog.write('%s,%s,%s\n' % (p1['bioguide_id'],ln1,fn1))
			if jpols2['count'] != 1:
				print (fn2, ln2, jpols2['count'])
			else:
				p2 = jpols2['results'][0]
				clog.write('%s,%s,%s\n' % (p2['bioguide_id'],ln2,fn2))
		else:
			ln,fn,st,dst = l.split(',')
			upols = urllib2.urlopen(url % (ln,fn,st))
			pols = upols.read()
			jpols = json.loads(pols)
			#print json.dumps(jpols, indent=4, sort_keys=True)
			if jpols['count'] != 1:
				print (l, jpols['count'])
			else:
				#print (l, jpols['count'])
				p = jpols['results'][0]
				clog.write('%s,%s,%s\n' % (p['bioguide_id'],ln,fn))
		sleep(1.00)
	print num_pols
	clog.close()


getCongress(113)

#B001228,Bono Mack,Mary
#B001276,Buerkle,Ann Marie
#C001072,Carson,Andre
#D000355,Dingell,John
#E000172,Emerson,Jo Ann
#G000551,Grijalva,Raul
#G000535,Gutierrez,Luis
#H001056,Herrera Beutler,Jaime
#H000636,Hinojosa,Ruben
#H001048,Hunter,Duncan
#J000032,Jackson Lee,Sheila
#J000255,Walter,Jones
#L000573,Labrador,Raul
#L000570,Lujan,Ben
#M001155,Mack,Connie
#M001159,McMorris Rodgers,Cathy
#M000725,Miller,George
#P000604,Payne,Donald
#S001156,Sanchez,Linda
#S000248,Serrano,Jose
#V000128,Van Hollen,Chris
#V000081,Velazquez,Nydia
#W000797,Wasserman Schultz,Debbie
#Y000031,Young,C.
#M000639,Menendez,Robert