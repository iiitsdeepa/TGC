import csv
from time import sleep

bioids = []
votes = []
ind_votes = []
print 'First the Politicians'
for congress in range(112,115):
	with open(str(congress)+'Politicians.csv') as csv_file:
		reader = csv_file.readlines()
		for row in reader:
			temp = row.split(',')
			tempbioid = temp[9]
			party = temp[1]
			fyio = temp[8]
			idexists = 0
			for bioid in bioids:
				if (bioid[0] == tempbioid):
					idexists = 1
			if (idexists == 0):
				if (len(bioids) == 0):
					bioids.append([tempbioid, party, fyio])
					continue
				else:
					for i in range(0,len(bioids)+1):
						if (i < len(bioids)):
							if (bioids[i][0] > tempbioid):
								bioids.insert(i,[tempbioid, party, fyio])
								break
						else:
							bioids.append([tempbioid, party, fyio])
							break
					continue
			else:
				continue

print 'Now the Ind_Votes csv file'
with open('ind_Voter_Table.csv') as csv_file:
	reader = csv_file.readlines()
	for row in reader:
		ind_votes.append(row.split(','))

print 'Now the All Votes csv file'
with open('votesall.csv') as csv_file:
	reader = csv_file.readlines()
	for row in reader:
		temp = row.split(',')
		temp[13] = temp[13][:-1]
		votes.append([temp[10], temp[11], temp[12], temp[13]]) 
		#temp[10] -> votes[i][0] = Total Vote, temp[11] -> votes[i][1] = GOP Vote, temp[12] -> votes[i][2] = Dem Vote, temp[13] -> votes[i][3] = Ind Vote

print 'Finally the output csv file'
with open('PoliticianStats.csv', 'w') as csv_file: #order of data in csv file: party loyalty, sponsored/cosponsored, attendance, yio, effectiveness
	for i in range(len(bioids)):
		bioid = bioids[i][0]
		pol_party = bioids[i][1]
		fyio = bioids[i][2]
		votes_in_party = 0
		total_votes = 0
		attendance = 0
		#for loop used to calculate the party loyalty and attendance
		print str(i)+' - '+bioid
		for j in range(len(ind_votes)):
			pol_vote = ind_votes[j][i+2]
			which_party = ''
			party_breakdown = []
			if pol_party == 'R':
				which_party = votes[j][1]
			elif pol_party == 'D':
				which_party = votes[j][2]
			elif pol_party == 'I':
				continue
			party_breakdown = which_party.split('_')
			party_vote = ''
			temp_break = 0
			if temp_break < int(party_breakdown[0]):
				temp_break = int(party_breakdown[0])
				party_vote = 'Y'
			if temp_break < int(party_breakdown[1]):
				temp_break = int(party_breakdown[1])
				party_vote = 'N'
			if temp_break < int(party_breakdown[3]):
				temp_break = int(party_breakdown[3])
				party_vote = 'P'
			if pol_vote == party_vote:
				votes_in_party += 1
			if pol_vote == 'NV':
				attendance += 1
			elif party_vote != '' and pol_vote != 'None':
				total_votes += 1
		if (pol_party == 'I' or total_votes == 0):
			attendance = 'N/A'
			party_loyalty = 'N/A'
		else:
			attendance = "%.1f" % (float(attendance) / float(total_votes) * 100)
			party_loyalty = "%.1f" % (float(votes_in_party) / float(total_votes) * 100)
		#this is used to calculate the number of sponsored and cosponsored bills and the effectiveness
		cosponsor_count = 0
		cosponsor_billid = []
		with open('cosponsorsall.csv') as second_file:
			reader = second_file.readlines()
			for each in reader:
				temp_line = each.split(',')
				temp_line[1] = temp_line[1][:-1]
				if temp_line[1] == bioid:
					cosponsor_count += 1
					cosponsor_billid.append(temp_line[0])
		
		sponsor_passed = 0
		sponsor_count = 0
		
		with open('bills_all.csv') as third_file:
			reader = third_file.readlines()
			for each in reader:
				temp_line = each.split('$$$')
				if temp_line[9] == bioid:
					sponsor_count += 1
					if temp_line[6] == 'True':
						if temp_line[8] == 'True':
							sponsor_passed += 1
				for bill in cosponsor_billid:
					if bill == temp_line[0]:
						if temp_line[6] == 'True':
							if temp_line[8] == 'True':
								sponsor_passed += 1
		
		if (sponsor_count + cosponsor_count) == 0:
			effectiveness = 0
		else:
			effectiveness = "%.1f" % (float(sponsor_passed) / float(sponsor_count + cosponsor_count) * 100)
		line = str(bioid)+','
		line += party_loyalty + ','
		line += str(sponsor_count) + ','
		line += str(cosponsor_count) + ','
		line += str(attendance) + ','
		line += str(2016-int(fyio)) + ','
		line += str(sponsor_passed) + ','
		line += str(effectiveness) + '\n'
		csv_file.write(line)