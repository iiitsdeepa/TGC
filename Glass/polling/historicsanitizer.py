#this program converts the raw txt files of congressional members, and converts them to CSV files of just first and last name

f = open('2016-national-gop-primary.csv')
n = open('111membs.csv', 'w')
#n = open('111membs.csv', 'w')
linenum = 0
for l in iter(f):
	if linenum != 0:
		u = l.split(',')
		for i in xrange(len(u)):
			if u[i] == '':
				u[i] = '-1'
		line = ','.join(map(str, u))
		print line
	linenum += 1

print linenum
    

f.close()
#n.close()