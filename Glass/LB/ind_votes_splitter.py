import csv

with open('ind_Voter_Table.csv', 'r') as inputcsv:
	string = 'indvotepart'
	for i in range(1, 43):
		reader = inputcsv.readlines()
		count = 1
		filenum = 1
		for row in reader:
			outfilestr = string+'%s.csv' % (filenum)
			print outfilestr
			with open(outfilestr, 'a') as output:
				output.write(row)
				count += 1
				if (count > 95):
					filenum += 1
					count = 1

