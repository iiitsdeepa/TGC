#This program takes data from the file congress_makeups.csv and inserts it into the database.
#The fields inserted are: start_year, num, hdems,hrepubs,hinds,sdems,srepubs,sinds

import urllib2
import json
import MySQLdb
from time import sleep

#connecting to the database
db = MySQLdb.connect(host="localhost", user="the_giver", passwd="memories", db="LegislativeBranch")
cursor = db.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()


#opening congress_makeups.csv and reading line by line
f = open('congress_makeups.csv')
for line in iter(f):
    syear,num,hdems,hrepubs,hinds,sdems,srepubs,sinds =line.split(',')
    print syear,num,hdems,hrepubs,hinds,sdems,srepubs,sinds
    sql1 = 'INSERT INTO Congress (start_year,num,hdems,hrepubs,hinds,sdems,srepubs,sinds) '
    sql2 = 'VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
    sql = sql1 + sql2
    cursor.execute(sql, (syear,num,hdems,hrepubs,hinds,sdems,srepubs,sinds))



#close out    
f.close()
cursor.close()
db.commit()
db.close()