import scipy.stats as ss
import numpy as np

def descriptiveStats(list):
	array = np.asarray(list)
	mean = array.mean()
	max = array.max()
	min = array.min()
	std = array.std()
	print 'min: %s max: %s, mean: %s, std: %s' %(min,max,mean,std)
	return min, max, mean, std

def getZ(list, mean, std):
	zlist = []
	for item in list:
		zscore = (item - mean) / std
		zlist.append(zscore)
	return zlist

def makeGrades(zlist, zmax):
	gradelist = []
	factor = 25.0 / float(zmax)
	print zmax, factor
	for item in zlist:
		grade = 75 + (item * factor)
		gradelist.append(grade)
	return gradelist


hr = 0
s = 1

#representatives
enacteda = []
sponsoreda = []
cosponsoreda = []
ployaltya = []
if hr == 1:
	with open('rep_li.csv', 'r') as reps:
		i= 0
		for rep in reps:
			bioguide_id, state, district, name, gender, party, fyio, fbid, twid, enacted, sponsored, cosponsored, ployalty = rep.split(',')
			yio = 2016 - int(fyio)
			
			enacteda.append(float(enacted)/yio)
			sponsoreda.append(float(sponsored)/yio)
			cosponsoreda.append(float(cosponsored)/yio)
			ployaltya.append(float(ployalty)/yio)
if s == 1:
	with open('sen_li.csv', 'r') as sens:
		i= 0
		for sen in sens:
			bioguide_id, state, rank, name, gender, party, fyio, fbid, twid, enacted, sponsored, cosponsored, ployalty = sen.split(',')
			yio = 2016 - int(fyio)
			
			enacteda.append(float(enacted)/yio)
			sponsoreda.append(float(sponsored)/yio)
			cosponsoreda.append(float(cosponsored)/yio)
			ployaltya.append(float(ployalty)/yio)	

#do the stats
print 'enacted stats:'
emin, emax, emean, estd = descriptiveStats(enacteda)
ez = getZ(enacteda, emean, estd)
ezmin, ezmax, ezmean, ezstd = descriptiveStats(ez)
egrades = makeGrades(ez, ezmax)
print 'sponsored stats:'
smin, smax, smean, sstd = descriptiveStats(sponsoreda)
sz = getZ(sponsoreda, smean, sstd)
szmin, szmax, szmean, szstd = descriptiveStats(sz)
sgrades = makeGrades(sz, szmax)
print 'co-sponsored stats:'
cmin, cmax, cmean, cstd = descriptiveStats(cosponsoreda)
cz = getZ(cosponsoreda, cmean, cstd)
czmin, czmax, czmean, czstd = descriptiveStats(cz)
cgrades = makeGrades(cz, czmax)
print 'party loyalty stats:'
pmin, pmax, pmean, pstd = descriptiveStats(ployaltya)

#create array of legislative indexes
i = 0
lis = []
for egrade in egrades:
	li = (egrade * .45) + (sgrades[i] * .35) + (cgrades[i] * .2)
	lis.append(li)
	i = i + 1

print('legislative indexes===========================')
lmin, lmax, lmean, lstd = descriptiveStats(lis)
lz = getZ(lis, lmean, lstd)
lzmin, lzmax, lzmean, lzstd = descriptiveStats(lz)
lgrades = makeGrades(lz, lzmax)
descriptiveStats(lgrades)

#loop through reps, create csv and legislative index
if hr == 1:
	rep_csv = open('repindex.csv', 'w')
	with open('rep_li.csv', 'r') as reps:
		i= 0
		for rep in reps:
			bioguide_id, state, district, name, gender, party, fyio, fbid, twid, enacted, sponsored, cosponsored, ployalty = rep.split(',')
			print bioguide_id, state, district, name, gender, party, fyio, fbid, twid, ployalty, egrades[i], sgrades[i], cgrades[i], lgrades[i]
			rep_csv.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'%(bioguide_id, state, district, name, gender, party, fyio, fbid, twid, int(ployalty), int(egrades[i]), int(sgrades[i]), int(cgrades[i]), int(lgrades[i])))
			i = i + 1
if s == 1:
	rep_csv = open('senindex.csv', 'w')
	with open('sen_li.csv', 'r') as sens:
		i= 0
		for sen in sens:
			bioguide_id, state, rank, name, gender, party, fyio, fbid, twid, enacted, sponsored, cosponsored, ployalty = sen.split(',')
			print bioguide_id, state, rank, name, gender, party, fyio, fbid, twid, ployalty, egrades[i], sgrades[i], cgrades[i], lgrades[i]
			rep_csv.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'%(bioguide_id, state, rank, name, gender, party, fyio, fbid, twid, int(ployalty), int(egrades[i]), int(sgrades[i]), int(cgrades[i]), int(lgrades[i])))
			i = i + 1