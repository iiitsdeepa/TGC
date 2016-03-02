import csv

bioids = []
outputpy = open('indVoterDatabase.py', 'w')
outputcsvpy = open('indVoterCSVProcess.py', 'w')
outputcsv = open('ind_Voter_Table.csv', 'w')
outputpy.write('class Ind_Votes(db.Model):\n\tbill_id = db.StringProperty(required = True)\n\troll_id = db.StringProperty(required = True)\n')
outputcsvpy.write('entry = Ind_Votes(bill_id = temp[0], roll_id = temp[1])\n')
for congress in range(112,115):
	csv_name = str(congress) + 'Politicians.csv'
	with open(csv_name) as csv_file:
		reader = csv_file.readlines()
		for row in reader:
			temp = row.split(',')
			tempbioid = temp[9]
			idexists = 0
			for bioid in bioids:
				if (bioid == tempbioid):
					idexists = 1
			if (idexists == 0):
				if (len(bioids) == 0):
					bioids.append(tempbioid)
					continue
				else:
					for i in range(0,len(bioids)+1):
						if (i < len(bioids)):
							if (bioids[i] > tempbioid):
								bioids.insert(i,tempbioid)
								break
						else:
							bioids.append(tempbioid)
							break
					continue
			else:
				continue
votestable = [[i for i in bioids]]
votestable[0].insert(0,'bill_id')
votestable[0].insert(1,'roll_id')
for congress in range(112,115):
	csv_name2 = 'ind_votes' + str(congress) + '.csv'
	with open(csv_name2) as indvotescsv:
		reader = indvotescsv.readlines()
		linecount = 0
		for row in reader:
			linecount += 1
			if (linecount%5000 == 0):
				print linecount
			temp = row.split(',')
			tempbioid = temp[2]
			tempbillid = temp[0]
			temprollid = temp[1]
			tempvote = temp[3]
			tempvote = tempvote[:-1]
			i = 0
			j = 2
			for row in votestable:
				if (row[0] == tempbillid and row[1] == temprollid):
					break
				else:
					i += 1
			if (i == len(votestable)):
				temprow = ['None' for z in votestable[0]]
				votestable.append(temprow)
				votestable[i].insert(0,tempbillid)
				votestable[i].insert(1,temprollid)
			for bioid in bioids:
				if (bioid == tempbioid):
					break
				else:
					j += 1
			votestable[i][j] = tempvote
for i in range(1,len(votestable)):
	line = ''
	for j in range(len(votestable[i])):	
		line += str('%s,' % (votestable[i][j]))
	line = line[:-1]
	line += '\n'
	outputcsv.write(line)
c = 2
for tempbioid in bioids:
	line = str('\t%s = db.StringProperty(required = False)\n' % (tempbioid))
	outputpy.write(line)	
	csvline = str('entry.%s = temp[%s]\n' % (tempbioid, str(c)))
	outputcsvpy.write(csvline)
	c += 1

outputpy.close()
outputcsvpy.close()
outputcsv.close()
