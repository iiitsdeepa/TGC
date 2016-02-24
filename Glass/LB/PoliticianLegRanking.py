import csv

def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/n # the population variance
    return pvar**0.5

master = []
sponsored = []
cosponsored = []
missedvotes = []
enacted = []
yio = []
bio = []
stdeviation = [0.0, 0.0, 0.0, 0.0]
zscores = []
with open('PoliticianStats.csv') as csv_file:
	reader = csv_file.readlines()
	for row in reader:
		row = row[:-1]
		temp = row.split(',')
		master.append(row)
		sponsored.append(float(temp[2]))
		cosponsored.append(float(temp[3]))
		enacted.append(float(temp[7]))
		yio.append(int(temp[5]))
		bio.append(temp[0])
		if (temp[4] != 'N/A'):
			missedvotes.append(float(temp[4]))
		else:
			missedvotes.append('N/A')
#calculate the average and standard of deviation
missedvotesedit = []
enactededit = []
for each in missedvotes:
	if each != 'N/A':
		missedvotesedit.append(each)
for each in enacted:
	if each != 'N/A':
		enactededit.append(each)
for i in range(707):
	if yio[i] >= 5:
		sponsored[i] = sponsored[i] / 3.0
		cosponsored[i] = cosponsored[i] / 3.0
	elif yio[i] >= 3:
		sponsored[i] = sponsored[i] / 2.0
		cosponsored[i] = cosponsored[i] / 2.0
averagespon = mean(sponsored)
averagecosp = mean(cosponsored)
averagemiss = mean(missedvotesedit)
averageenac = mean(enactededit)
stdevspon = pstdev(sponsored)
stdevcosp = pstdev(cosponsored)
stdevmiss = pstdev(missedvotesedit)
stdenac = pstdev(enactededit)
#now calculate the z scores
maxzscore = [0.0, 0.0, 0.0, 0.0]
#all z-scores are set with an average of 75 and a max z-score of 100
#the missed_votes is different since a lower z-score is better.
#in this case, the z score is reversed (score*-1) and then the new highest z-score is set to 100. 
#since not many congressmen miss votes, the average is usually between 90 and 95, with some as low as 50
for i in range(len(sponsored)):#First do the sponsor z-scores
	sponsored[i] = (sponsored[i] - averagespon) / stdevspon
	if sponsored[i] > 5.0:
		sponsored[i] = 5.0
	sponsored[i] = (sponsored[i]*5)+50
	if (sponsored[i] > maxzscore[0]):
		maxzscore[0] = sponsored[i]
for i in range(len(cosponsored)):#then the cosponsor z-scores
	cosponsored[i] = (cosponsored[i] - averagecosp) / stdevcosp
	if cosponsored[i] > 5.0:
		cosponsored[i] = 5.0
	cosponsored[i] = (cosponsored[i]*5)+50
	if (cosponsored[i] > maxzscore[1]):
		maxzscore[1] = cosponsored[i]
for i in range(len(missedvotes)):#this is the first step of calculating the missed votes. 
	if missedvotes[i] == 'N/A':
		continue
	missedvotes[i] = (missedvotes[i] - averagemiss) / stdevmiss
	if missedvotes[i] > 7.0:
		missedvotes[i] = 7.0
	missedvotes[i] = (missedvotes[i]*(0-8))
	if (missedvotes[i] > maxzscore[2]):
		maxzscore[2] = missedvotes[i]
for i in range(len(enacted)):#enacted scores are calculated last
	if enacted[i] == 'N/A':
		continue
	enacted[i] = (enacted[i] - averageenac) / stdenac
	if enacted[i] > 5.0:
		enacted[i] = 5.0
	enacted[i] = (enacted[i]*5)+50
	if (enacted[i] > maxzscore[3]):
		maxzscore[3] = enacted[i]
for i in range(len(missedvotes)):#this is the second step of calculting missed votes, setting each score on the 100 scale
	if missedvotes[i] == 'N/A':
		continue
	missedvotes[i] = missedvotes[i] + (100 - maxzscore[2])

with open('PoliticianStatsComplete.csv', 'w') as csv_file:
	legislative_score = []
	for i in range(707):
		if (missedvotes[i] == 'N/A'):
			temp = float(sponsored[i])*0.375 + float(cosponsored[i])*0.375 + float(enacted[i])*0.25
			legislative_score.append(temp)
		else:
			temp = float(sponsored[i])*0.3 + float(cosponsored[i])*0.3 + float(missedvotes[i])*0.2 + float(enacted[i])*0.2
			legislative_score.append(temp)
	aveleg = mean(legislative_score)
	stdleg = pstdev(legislative_score)
	maxleg = 0.0
	minleg = 0.0
	for i in range(707):
		legislative_score[i] = (legislative_score[i] - aveleg) / stdleg
		#print legislative_score[i],
		if legislative_score[i] > maxleg:
			maxleg = legislative_score[i]
		if legislative_score[i] < minleg:
			minleg = legislative_score[i]
	minleg = 0-minleg
	#print ''
	#print maxleg, minleg
	for i in range(707):
		if legislative_score[i] > 0:
			legislative_score[i] = (legislative_score[i] * (50/maxleg)) + 50
		else:
			legislative_score[i] = (legislative_score[i] * (50/minleg)) + 50
	for i in range(707):
		if missedvotes[i] == 'N/A':
			csv_file.write(master[i] +','+ str('%.2f,%.2f,%.2f,%.2f,') % (legislative_score[i],sponsored[i],cosponsored[i],enacted[i]) +'N/A,\n')
		else:
			csv_file.write(master[i] +','+ str('%.2f,%.2f,%.2f,%.2f,%.2f,') % (legislative_score[i],sponsored[i],cosponsored[i],enacted[i],missedvotes[i]) +'\n')
with open('PoliticianStatsSubscores.csv', 'w') as csv_file:
	for i in range(707):
		csv_file.write(bio[i] +','+ str(sponsored[i]) +','+ str(cosponsored[i]) +','+ str(missedvotes[i]) +','+ str(enacted[i]) +','+ str('%.2f') % (legislative_score[i]) + ',\n')