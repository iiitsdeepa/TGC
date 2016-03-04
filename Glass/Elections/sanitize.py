n = open('primary.csv', 'w')
with open('primary.tsv') as f:
	for line in f:
		t = line.replace('\t',',')
		n.write(t)

f.close()
n.close()