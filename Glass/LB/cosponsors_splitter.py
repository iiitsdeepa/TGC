import csv

with open('cosponsors112.csv', 'r') as inputcsv:
	string = 'cosponsor112part'
	for i in range(1, 12):
		reader = inputcsv.readlines()
		count = 1
		filenum = 1
		for row in reader:
			outfilestr = string+'%s.csv' % (filenum)
			print outfilestr
			with open(outfilestr, 'a') as output:
				output.write(row)
				count += 1
				if (count > 10000):
					filenum += 1
					count = 1
with open('cosponsors113.csv', 'r') as inputcsv:
	string = 'cosponsor113part'
	for i in range(1, 13):
		reader = inputcsv.readlines()
		count = 1
		filenum = 1
		for row in reader:
			outfilestr = string+'%s.csv' % (filenum)
			print outfilestr
			with open(outfilestr, 'a') as output:
				output.write(row)
				count += 1
				if (count > 10000):
					filenum += 1
					count = 1
with open('cosponsors114.csv', 'r') as inputcsv:
	string = 'cosponsor114part'
	for i in range(1, 10):
		reader = inputcsv.readlines()
		count = 1
		filenum = 1
		for row in reader:
			outfilestr = string+'%s.csv' % (filenum)
			print outfilestr
			with open(outfilestr, 'a') as output:
				output.write(row)
				count += 1
				if (count > 10000):
					filenum += 1
					count = 1