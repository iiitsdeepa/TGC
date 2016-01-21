
splittee = 'bills113.csv'

csv = open(splittee, 'r')



lines = csv.read().split('\n')
num_lines = len(lines)
temp_size = 1000
num_temps = num_lines / temp_size + 1

print num_lines, temp_size, num_temps

#open temp csv files
temp = []
for x in xrange(0, num_temps):
	tempname = 'temp'+str(x)+'.csv'
	a = open(tempname,'w')
	temp.append(a)

x = 0
for l in lines:
	tempindex = x / temp_size
	temp[tempindex].write(l+'\n')
	x+=1


#close temp csv files
for x in xrange(0, num_temps):
	temp[x].close()




	

