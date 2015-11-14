import urllib2
import json
import MySQLdb
from time import sleep

#connecting to the database
db = MySQLdb.connect(host="localhost", user="the_giver", passwd="memories", db="political_database")
cursor = db.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

#opening log file
log_file = open('billapidata.txt', 'a')
log_file.write('--------------------------------------------------------------------\n')


'''
NOTE: This script must be run once per congress. Choose which congress by changing the congress varaible
NOTE: for each congress, it must be run for s, sres, sjres, sconres. CHANGE TABLES ACCORDINGLY
'''

billtype_convert = {'1':'hr', '2':'hres', '3':'hjres', '4':'hconres', '5':'s', '6':'sres', '7':'sjres', '8':'sconres'}
bill_url = 'https://congress.api.sunlightfoundation.com/bills?fields=bill_id,introduced_on,last_vote_at,official_title,popular_title,short_title,nicknames,keywords,summary_short,urls,enacted_as,sponsor_id,cosponsor_ids,cosponsor_count,keywords&%s&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
congress = 115

start_year = 2015
get_bills = 1
get_votes = 1
fixer = 1

sql = 'INSERT INTO Congress (number) VALUES(%s)'
cursor.execute(sql, (congress))
if get_bills == 1:
	#loop through each type
	k = 1
	while k <= 8:
		if k < 5:
			table = 'House_Bills'
			id_type = 'hrbill_id'
			cosponsor_table = 'House_Cosponsorships'
			politician_table = 'Representatives'
			key_table = 'Hbill_Keywords'
		else:
			table = 'Senate_Bills'
			id_type = 'sbill_id'
			cosponsor_table = 'Senate_Cosponsorships'
			politician_table = 'Senators'
			key_table = 'Sbill_Keywords'
		
		bill_type = billtype_convert['%s' % k]

		#open json to get total count and num_pages
		bill_method = 'congress=%d&bill_type=%s&per_page=50' % (congress, bill_type)
		ubills = urllib2.urlopen(bill_url % bill_method)
		bills = ubills.read()
		jbills = json.loads(bills)
		total_bills = jbills['count']
		per_page = 50
		num_pages = (total_bills / per_page) + 2

		#insert bill number data into congress
		sql1 = 'UPDATE Congress SET %s=' % bill_type
		sql2 = '%s WHERE number = %s'
		sql = sql1 + sql2
		cursor.execute(sql, (total_bills, congress))
		
		print 'WORKING ON %s, NUM_PAGES = %s' % (bill_type, num_pages)

		#loop through each page received from api
		i = 0
		while i < num_pages: #num_pages
			bill_method = 'congress=%d&bill_type=%s&per_page=50&page=%d' % (congress, bill_type, i)
			ubills = urllib2.urlopen(bill_url % bill_method)
			bills = ubills.read()
			jbills = json.loads(bills)
			print 'STARTING PAGE %d' % i

			#loop through each bill, populating all tables associated
			j = 0
			while j < jbills['page']['count']: #50
				
				#pull data for bill creation
				bill_id = jbills['results'][j]['bill_id'].encode('utf-8')
				official_title = jbills['results'][j]['official_title'].encode('utf-8')
				try:
					short_title = jbills['results'][j]['short_title'].encode('utf-8')
				except:
					short_title = 'none'
				try:
					popular_title = jbills['results'][j]['popular_title'].encode('utf-8')
				except:
					popular_title = 'none'
				try:
					nickname = jbills['results'][j]['nicknames'][0].encode('utf-8')
				except:
					nickname = 'none'
				try:
					summary_short = jbills['results'][j]['summary_short'].encode('utf-8')
				except:
					summary_short = 'none'
				try:
					link = jbills['results'][j]['urls']['congress'].encode('utf-8')
				except:
					link = 'none'
				try:
					sponsor_id = jbills['results'][j]['sponsor_id'].encode('utf-8')
				except:
					sponsor_id = 'none'

				#check to see if bill already exists in its respective table (insert if it does not)
				sql1 = 'SELECT * FROM %s WHERE %s ' % (table, id_type)
				sql2 = '= %s'
				sql = sql1 + sql2
		 		cursor.execute(sql, (bill_id))
		 		unique = cursor.rowcount
		 		if unique == 0:
		 			#see if the sponsor is a current member of congress
					sql1 = 'SELECT bioguide_id FROM %s ' % politician_table
					sql2 = 'WHERE bioguide_id = %s'
					sql = sql1 + sql2
					cursor.execute(sql, (sponsor_id))
					results = cursor.rowcount
					if results == 0:
						#sponsor doesn't exist in congress, keep sponsor vacant in bill table
						sql1 = 'INSERT INTO %s (%s, bill_type, congress, official_title, short_title, popular_title, nickname, summary_short, link) ' % (table, id_type)
		 				sql2 = 'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		 				sql = sql1 + sql2
		 				cursor.execute(sql, (bill_id, bill_type, congress, official_title, short_title, popular_title, nickname, summary_short, link))
					else:
						#sponsor exists in congress, insert sponsor with bill
			 			sql1 = 'INSERT INTO %s (%s, bill_type, congress, official_title, short_title, popular_title, nickname, summary_short, link, sponsor) ' % (table, id_type)
			 			sql2 = 'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
			 			sql = sql1 + sql2
			 			cursor.execute(sql, (bill_id, bill_type, congress, official_title, short_title, popular_title, nickname, summary_short, link, sponsor_id))
					
				#KEYWORD STUFF (making new keywords, and associating bill with keywords)
				keywords = jbills['results'][j]['keywords']
				for u in keywords:
					#check to see if keyword exists
					sql = 'SELECT * FROM Keywords WHERE keyword=%s'
					cursor.execute(sql, (u))
					results = cursor.rowcount
					if results == 0:
						#keyword doesn not exist, insert keyword
						sql = 'INSERT INTO Keywords (keyword) VALUES(%s)'
						cursor.execute(sql, (u))

					#check to see that keyword-bill association doesn't already exist
					sql1 = 'SELECT * FROM %s ' % key_table
					sql2 = 'WHERE bill = %s AND keyword = %s'
					sql = sql1 + sql2
					cursor.execute(sql, (bill_id, u))
					results = cursor.rowcount
					if results == 0:
						#keyword-bill association doesn't exist, insert keyword-bill association
						sql1 = 'INSERT INTO %s (bill, keyword)' % key_table
						sql2 = 'VALUES(%s,%s)'
						sql = sql1+sql2
						cursor.execute(sql, (bill_id, u))

				#COSPONSOR STUFF
				cosponsor_ids = jbills['results'][j]['cosponsor_ids']
				if cosponsor_ids:			
					for u in cosponsor_ids:
						#see if the cosponsor is a current member of congress
						sql1 = 'SELECT bioguide_id FROM %s ' % politician_table
						sql2 = 'WHERE bioguide_id = %s'
						sql = sql1 + sql2
						cursor.execute(sql, (u))
						member = cursor.rowcount
						#see if the entry already exists
						sql1 = 'SELECT * FROM %s ' % cosponsor_table
						sql2 = 'WHERE bioguide_id = %s and bill_id = %s'
						sql = sql1 + sql2
						cursor.execute(sql, (u, bill_id))
						unique = cursor.rowcount
						if member != 0 and unique == 0:
							sql1 = 'INSERT INTO %s (bioguide_id, bill_id) ' % cosponsor_table
							sql2 = 'VALUES(%s,%s)'
							sql = sql1 + sql2
							cursor.execute(sql, (u, bill_id))
				j += 1
				print j,
				db.commit()
			print 'COMPLETED PAGE: %d' % i
			db.commit()
			i += 1
			sleep(1.00)
		k += 1

'''
-----------------------------------------Vote Stuff-------------------------------------
'''


vote_url = 'https://congress.api.sunlightfoundation.com/votes?fields=bill_id,roll_id,chamber,question,result,breakdown,voter_ids,voters.vote&%s&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'

if get_votes == 1:
	print 'WORKING ON VOTES STUFF'
	chambers = ['house', 'senate']
	for chamber in chambers:
		vote_method = 'congress=%d&chamber=%s' % (congress, chamber)
		uvotes = urllib2.urlopen(vote_url % vote_method)
		votes = uvotes.read()
		jvotes = json.loads(votes)
		total_votes = jvotes['count']
		per_page = 50
		num_pages = (total_votes / per_page) + 1
		print 'NUM PAGES IS %s' % num_pages
		i = 0
		while i < num_pages:
			vote_method = 'congress=%d&chamber=%s&per_page=50&page=%d' % (congress, chamber, i)
			uvotes = urllib2.urlopen(vote_url % vote_method)
			votes = uvotes.read()
			jvotes = json.loads(votes)
			print 'STARTING PAGE %d' % i
			#loop through received bills
			j = 0
			while j < 50:
				if chamber == 'house':
					ivote_table = 'Individual_HVotes'
					politician_table = 'Representatives'
					bill_table = 'House_Bills'
					bill_id_type = 'hrbill_id'
				else:
					ivote_table = 'Individual_SVotes'
					politician_table = 'Senators'
					bill_table = 'Senate_Bills'
					bill_id_type = 'sbill_id'
				
				#get data from json
				vote_id = jvotes['results'][j]['roll_id']
				#see if vote already exists in database(if it does, continue)
				sql = 'SELECT vote_id FROM Vote_Breakdowns WHERE vote_id = %s'
				cursor.execute(sql, (vote_id))
				results = cursor.rowcount
				if results != 0:
					j += 1
					continue
				try:
					bill_id = jvotes['results'][j]['bill_id']
				except:
					j += 1
					continue
				
				#see if bill exists
				sql1 = 'SELECT * FROM %s WHERE %s ' % (bill_table, bill_id_type)
				sql2 = ' = %s'
				sql = sql1 + sql2
				cursor.execute(sql, (bill_id))
				bill_exist = cursor.rowcount
				if bill_exist == 0:
					log_file.write(bill_id)
					j += 1
					continue
				
				question = jvotes['results'][j]['question']
				tresult = jvotes['results'][j]['result']
				if tresult == 'Passed' or tresult == 'Bill Passed':
					result = 'P'
				else:
					result = 'F'
				total_yea = jvotes['results'][j]['breakdown']['total']['Yea']
				total_nay = jvotes['results'][j]['breakdown']['total']['Nay']
				total_abstain = jvotes['results'][j]['breakdown']['total']['Not Voting']
				D_yea = jvotes['results'][j]['breakdown']['party']['D']['Yea']
				D_nay = jvotes['results'][j]['breakdown']['party']['D']['Nay']
				D_abstain = jvotes['results'][j]['breakdown']['party']['D']['Not Voting']
				R_yea = jvotes['results'][j]['breakdown']['party']['R']['Yea']
				R_nay = jvotes['results'][j]['breakdown']['party']['R']['Nay']
				R_abstain = jvotes['results'][j]['breakdown']['party']['R']['Not Voting']
				try:
					I_yea = jvotes['results'][j]['breakdown']['party']['I']['Yea']
				except:
					I_yea = 0
				try:
					I_nay = jvotes['results'][j]['breakdown']['party']['I']['Nay']
				except:
					I_nay = 0
				try:
					I_abstain = jvotes['results'][j]['breakdown']['party']['I']['Not Voting']
				except:
					I_abstain = 0
				voter_ids = jvotes['results'][j]['voter_ids']

				#insert into database
				if chamber == 'house':
					cc = 'H'	
					sql1 = 'INSERT INTO Vote_Breakdowns (vote_id, bill_id, chamber, question, result, total_yea, total_nay, total_abstain, D_yea, D_nay, D_abstain, R_yea, R_nay, R_abstain, I_yea, I_nay, I_abstain, hrbill_id)'
					sql2 = 'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
				else:
					cc = 'S'
					sql1 = 'INSERT INTO Vote_Breakdowns (vote_id, bill_id, chamber, question, result, total_yea, total_nay, total_abstain, D_yea, D_nay, D_abstain, R_yea, R_nay, R_abstain, I_yea, I_nay, I_abstain, sbill_id)'
					sql2 = 'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

				sql = sql1 + sql2
				cursor.execute(sql, (vote_id, bill_id, cc, question, result, total_yea, total_nay, total_abstain, D_yea, D_nay, D_abstain, R_yea, R_nay, R_abstain, I_yea, I_nay, I_abstain, bill_id))
			
				#loop through individual votes and add to database
				for u in voter_ids:
					#check to see if the voter is in the database and the bill is in the database
					sql1 = 'SELECT * FROM %s ' %politician_table
					sql2 = 'WHERE bioguide_id = %s'
					sql = sql1 + sql2
					cursor.execute(sql, (u))				
					politician = cursor.rowcount
					sql1 = 'SELECT * FROM %s WHERE %s ' % (bill_table, bill_id_type)
					sql2 = ' = %s'
					sql = sql1 + sql2
					cursor.execute(sql, (u))
					bill_exist = cursor.rowcount
					if politician != 0:
						sql1 = 'INSERT INTO %s (bioguide_id, bill_id, vote_id, vote, congress)' % ivote_table
						sql2 = 'VALUES (%s, %s, %s, %s,%s)'
						sql = sql1 + sql2
						if voter_ids['%s'%u] == 'Yea':
							vote_cast = 'Y'
						elif voter_ids['%s'%u] == 'Nay':
							vote_cast = 'N'
						else:
							vote_cast = 'A'
						cursor.execute(sql, (u, bill_id, vote_id, vote_cast, congress))


				print j,

			sleep(1.00)

			i += 1

if fixer == 1:
	#fix the congress:
	sql = 'SELECT * FROM Congress WHERE number = %s'
	cursor.execute(sql, (congress))
	congress_results = cursor.fetchone()
	hbills_total = congress_results[3] +  congress_results[4] + congress_results[5] + congress_results[6]
	sbills_total = congress_results[8] +  congress_results[9] + congress_results[10] + congress_results[11]
	sql = 'UPDATE Congress SET start_year = %s, total_hbills = %s, total_sbills = %s WHERE number = %s'
	cursor.execute(sql, (start_year, hbills_total, sbills_total, congress))

	#get voted on and enacted for each bill
	chambers = ['House_Bills', 'Senate_Bills']
	for chamber in chambers:
		if chamber == 'House_Bills':
			id_type = 'hrbill_id'
		else:
			id_type = 'sbill_id'
		sql = 'SELECT bill_id, result FROM Vote_Breakdowns'
		cursor.execute(sql)
		breakdowns = cursor.fetchall()
		for breakdown in breakdowns:
			if breakdown[1] == 'P':
				sql1 = 'UPDATE %s SET voted_on=\'Y\', passed=\'Y\' WHERE %s' % (chamber, id_type)
				sql2 = '=%s'
			else:
				sql1 = 'UPDATE %s SET voted_on=\'Y\', passed=\'N\' WHERE %s' % (chamber, id_type)
				sql2 = '=%s'
			sql = sql1 + sql2
			cursor.execute(sql, (breakdown[0]))



#close out
log_file.close()
cursor.close()
db.commit()
db.close()