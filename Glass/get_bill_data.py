import urllib2
import json
import os
import re

#======================================================sunlight stuff====================
sunlight_key = '5a2e18d2e3ed4861a8604e9a5f96a47a'
bills_url = 'https://congress.api.sunlightfoundation.com//bills?congress=111&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'

bil = urllib2.urlopen(bills_url)
bill = bil.read()
j_bill = json.loads(bill)

print json.dumps(j_bill, indent=4, sort_keys=True)
