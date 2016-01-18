import csv

bioids = []
outputpy = open('indVoterDatabase.py', 'w')
outputcsv = open('ind_Voter_Table.csv', 'w')
outputpy.write('class Ind_Votes(db.Model):\n\tbill_id = db.StringProperty(required = True)\n')
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
votestable[0][0] = 'bill_id'
for congress in range(112,115):
	csv_name2 = 'ind_votes' + str(congress) + '.csv'
	with open(csv_name2) as indvotescsv:
		reader = indvotescsv.readlines()
		for row in reader:
			temp = row.split(',')
			tempbioid = temp[1]
			tempbillid = temp[0]
			tempvote = temp[2]
			tempvote = tempvote[:-1]
			i = 0
			j = 0
			for row in votestable:
				if (row[0] == tempbillid):
					break
				else:
					i += 1
			if (i == len(votestable)):
				temprow = ['None' for z in votestable[0]]
				votestable.append(temprow)
				votestable[i][0] = tempbillid
			for bioid in bioids:
				if (bioid == tempbioid):
					break
				else:
					j += 1
			print votestable
			print i 
			print j
			votestable[i][j] = tempvote
			if (i > 5):
				break
	break
for i in votestable:
	line = ''
	for j in votestable[i]:	
		line += str('%s,' % (votestable[i][j]))
	line = line[:-1]
	line += '\n'
	outputpy.write(line)
for tempbioid in bioids:	
	line = str('\t%s = db.StringProperty(required = False)\n' % (tempbioid))
	outputpy.write(line)

outputpy.close()
outputcsv.close()
