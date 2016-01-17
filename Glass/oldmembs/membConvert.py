#this program converts the raw txt files of congressional members, and converts them to CSV files of just first and last name

f = open('111raw.txt')
n = open('111membs.csv', 'w')
for l in iter(f):
    names = l.split(' (')
    lnames, fnames = names[0].split(', ')
    b = lnames.split(' ')
    lname = b[len(b)-1]
    a = fnames.split(' ')
    fname = a[0]
    line = '%s,%s\n' % (lname,fname)
    n.write(line)
    print line
    

f.close()
n.close()