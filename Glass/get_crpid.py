
rep = 0
sen = 0

if rep == 1:
	#opening rep donors file
	rcrpfile = open('rep_crpids.txt', 'a')

	url = 'http://www.opensecrets.org/api/?method=getLegislators&id=LA&output=json&apikey=ef5e75a0fc095fa58238c4ffb40d29f1'
	ucid = urllib2.urlopen(bill_url % bill_method)
	cid = ucid.read()
	jcid = json.loads(cid)
	print 'doing the thing'
	print jcid

	#closing rep donors file
	rcrpfile.close()

if sen == 1:
	#opening rep donors file
	scrpfile = open('sen_crpids.txt', 'a')

	#closing rep donors file
	scrpfile.close()
