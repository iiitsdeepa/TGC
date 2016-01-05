#this program converts the raw txt files of congressional members, and converts them to CSV files of just first and last name

f = open('2016-national-gop-primary.csv')
#n = open('111membs.csv', 'w')
linenum = 0
for l in iter(f):
	if linenum != 0:
		u = l.split(',')
		for d in u:
			if d == '':
				d = '-1'
		print u
	linenum += 1

print linenum
    

f.close()
#n.close()