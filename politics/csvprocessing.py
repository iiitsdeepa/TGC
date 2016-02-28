import os
import re
import random
import hashlib
import hmac
import urllib2
import json
import pdb
import logging
import random, string
from string import letters
import csv
import datetime

import webapp2
import jinja2
import cgi
from time import sleep
from google.appengine.ext.webapp.util import run_wsgi_app
from datetime import datetime, date, time

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.db import GqlQuery
from google.appengine.api import mail
from politics import *
from databaseclasses import *

#------------------------File Processing----------------------------

def process_visualization_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        temp = row_str.split(',')
        namequery = GqlQuery("SELECT * FROM Visualization WHERE bioguide_id = :1", temp[0])
        tempqueryrow = namequery.get()
        if tempqueryrow is None:
            entry = Visualization(name=temp[0],vtype=temp[1],title=temp[2],xaxis=temp[3],yaxis=temp[4],color=temp[5],query_columns=temp[6],element=temp[7],query=temp[8])
            entry.put()

def process_candidate_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        temp = row_str.split(',')
        namequery = GqlQuery("SELECT * FROM Candidate WHERE bioguide_id = :1", temp[0])
        tempqueryrow = namequery.get()
        if tempqueryrow is None:
            entry = Candidate(name=temp[0],party=temp[1],delegates=int(temp[2]),superdelegates=int(temp[3]))
            entry.put()

def process_state_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        name, abb, num, ss, js = row_str.split(',')
        entry = State(name=name, abbreviation=abb, num_districts=int(num), senior_senator=ss, junior_senator=js)
        entry.put()

def process_district_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        rep, state, num = row_str.split(',')
        entry = District(representative=rep, state=state, num=int(num))
        entry.put()

def process_senator_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        id, state, rank, name, gender, party, fyio, fbid, twid, ployalty, enacted, sponsored, cosponsored, li = row_str.split(',')
        entry = Senator(bioguide_id=id, state=state, rank=rank, name=name.decode('latin-1'), gender=gender, party=party, fyio=int(fyio), fbid=fbid, twid=twid, ployalty=int(ployalty), enacted=int(enacted), sponsored=int(sponsored), cosponsored=int(cosponsored), li=int(li))
        entry.put()

def process_rep_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        id, state, district, name, gender, party, fyio, fbid, twid, ployalty, enacted, sponsored, cosponsored, li = row_str.split(',')
        entry = Representative(bioguide_id=id, state=state, district=int(district), name=name.decode('latin-1'), gender=gender, party=party, fyio=int(fyio), fbid=fbid, twid=twid, ployalty=int(ployalty), enacted=int(enacted), sponsored=int(sponsored), cosponsored=int(cosponsored), li=int(li))
        entry.put()

def process_stat_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        id, total_votes, votes_wp, party_loyalty, sponsored_bills, cosponsored_bills = row_str.split(',')
        entry = Stat(bioguide_id=id, total_votes=int(total_votes), votes_wp=int(votes_wp), party_loyalty=float(party_loyalty), sponsored_bills=int(sponsored_bills), cosponsored_bills=int(cosponsored_bills))
        entry.put()

def process_politician_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        temp = row_str.split(',')
        bioidquery = GqlQuery("SELECT * FROM Politician WHERE bioguide_id = :1", temp[9])
        tempqueryrow = bioidquery.get()
        if tempqueryrow is None:
            entry = Politician(in_office=temp[0],party=temp[1],gender=temp[2],state=temp[3],state_name=temp[4],distrank=temp[5],chamber=temp[6],birthday=temp[7],fyio=int(temp[8]),bioguide_id=temp[9],crp_id=temp[10],fec_ids=temp[11],name=temp[12],phone=temp[13],website=temp[14],contact_form=temp[15],twitter_id=temp[16],youtube_id=temp[17],facebook_id=temp[18])
            entry.put()

def process_cosponsor_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    count = 0
    entry = []
    for row in reader:
        count += 1
        if (count%1000 == 0):
            logging.error(str(count))
        row_str = row[0]
        temp = row_str.split(',')
        #bioidquery = GqlQuery("SELECT * FROM Cosponsor WHERE bill_id = :1 AND bioguide_id = :2", temp[0], temp[1])
        #tempqueryrow = bioidquery.get()
        #if tempqueryrow is None:
        entry.append(Cosponsor(bill_id=temp[0],bioguide_id=temp[1]))
    db.put(entry)

def process_bill_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    count = 1
    for row in reader:
        if (count%500 == 0):
            logging.error(str(count))
        row_str = row[0]
        temp = row_str.split('$$$')
        bioidquery = GqlQuery("SELECT * FROM Bill WHERE bill_id = :1", temp[0])
        try:
            last_action = datetime.strptime(temp[11], '%Y-%m-%d')
        except:
            last_action = datetime.strptime(temp[11], '%Y-%m-%dT%H:%M:%SZ')
        try:
            introduced = datetime.strptime(temp[10], '%Y-%m-%d')
        except:
            introduced = datetime.strptime(temp[10], '%Y-%m-%dT%H:%M:%SZ')
        tempqueryrow = bioidquery.get()
        count += 1
        if tempqueryrow is None:
            entry = Bill(bill_id=temp[0],official_title=temp[1],popular_title=temp[2],short_title=temp[3],nicknames=temp[4],url=temp[5],active=temp[6],vetoed=temp[7],enacted=temp[8],sponsor_id=temp[9], introduced=introduced, last_action=last_action, last_updated=datetime.today())
            entry.put()

def process_votes_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        temp = row_str.split(',')
        entry = Votes(bill_id=temp[0],rid=temp[1],congress=temp[2],voted_at=temp[3],vote_type=temp[4],roll_type=temp[5],question=temp[6],required=temp[7],result=temp[8],source=temp[9],breakdown=temp[10],break_gop=temp[11],break_dem=temp[12],break_ind=temp[13])
        entry.put()

def process_ind_votes_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    count = 0
    for row in reader:
        count += 1
        if (count%100 == 0):
            break
            #logging.error(count)
        row_str = row[0]
        temp = row_str.split(',')
        entry = Ind_Votes(bill_id = temp[0], roll_id = temp[1])
        entry.A000022 = temp[2]
        entry.A000055 = temp[3]
        entry.A000069 = temp[4]
        entry.A000210 = temp[5]
        entry.A000358 = temp[6]
        entry.A000360 = temp[7]
        entry.A000361 = temp[8]
        entry.A000362 = temp[9]
        entry.A000365 = temp[10]
        entry.A000366 = temp[11]
        entry.A000367 = temp[12]
        entry.A000368 = temp[13]
        entry.A000369 = temp[14]
        entry.A000370 = temp[15]
        entry.A000371 = temp[16]
        entry.A000372 = temp[17]
        entry.A000373 = temp[18]
        entry.A000374 = temp[19]
        entry.B000013 = temp[20]
        entry.B000208 = temp[21]
        entry.B000213 = temp[22]
        entry.B000220 = temp[23]
        entry.B000243 = temp[24]
        entry.B000287 = temp[25]
        entry.B000410 = temp[26]
        entry.B000461 = temp[27]
        entry.B000468 = temp[28]
        entry.B000490 = temp[29]
        entry.B000574 = temp[30]
        entry.B000575 = temp[31]
        entry.B000589 = temp[32]
        entry.B000652 = temp[33]
        entry.B000711 = temp[34]
        entry.B000755 = temp[35]
        entry.B000911 = temp[36]
        entry.B000944 = temp[37]
        entry.B001135 = temp[38]
        entry.B001149 = temp[39]
        entry.B001227 = temp[40]
        entry.B001228 = temp[41]
        entry.B001230 = temp[42]
        entry.B001231 = temp[43]
        entry.B001232 = temp[44]
        entry.B001234 = temp[45]
        entry.B001236 = temp[46]
        entry.B001242 = temp[47]
        entry.B001243 = temp[48]
        entry.B001244 = temp[49]
        entry.B001245 = temp[50]
        entry.B001248 = temp[51]
        entry.B001250 = temp[52]
        entry.B001251 = temp[53]
        entry.B001252 = temp[54]
        entry.B001254 = temp[55]
        entry.B001255 = temp[56]
        entry.B001256 = temp[57]
        entry.B001257 = temp[58]
        entry.B001259 = temp[59]
        entry.B001260 = temp[60]
        entry.B001261 = temp[61]
        entry.B001262 = temp[62]
        entry.B001265 = temp[63]
        entry.B001267 = temp[64]
        entry.B001268 = temp[65]
        entry.B001269 = temp[66]
        entry.B001270 = temp[67]
        entry.B001271 = temp[68]
        entry.B001272 = temp[69]
        entry.B001273 = temp[70]
        entry.B001274 = temp[71]
        entry.B001275 = temp[72]
        entry.B001276 = temp[73]
        entry.B001277 = temp[74]
        entry.B001278 = temp[75]
        entry.B001279 = temp[76]
        entry.B001280 = temp[77]
        entry.B001281 = temp[78]
        entry.B001282 = temp[79]
        entry.B001283 = temp[80]
        entry.B001284 = temp[81]
        entry.B001285 = temp[82]
        entry.B001286 = temp[83]
        entry.B001287 = temp[84]
        entry.B001288 = temp[85]
        entry.B001289 = temp[86]
        entry.B001290 = temp[87]
        entry.B001291 = temp[88]
        entry.B001292 = temp[89]
        entry.B001293 = temp[90]
        entry.B001294 = temp[91]
        entry.B001295 = temp[92]
        entry.B001296 = temp[93]
        entry.B001297 = temp[94]
        entry.C000059 = temp[95]
        entry.C000071 = temp[96]
        entry.C000127 = temp[97]
        entry.C000141 = temp[98]
        entry.C000174 = temp[99]
        entry.C000266 = temp[100]
        entry.C000286 = temp[101]
        entry.C000380 = temp[102]
        entry.C000537 = temp[103]
        entry.C000542 = temp[104]
        entry.C000556 = temp[105]
        entry.C000560 = temp[106]
        entry.C000567 = temp[107]
        entry.C000705 = temp[108]
        entry.C000714 = temp[109]
        entry.C000754 = temp[110]
        entry.C000794 = temp[111]
        entry.C000880 = temp[112]
        entry.C000984 = temp[113]
        entry.C001035 = temp[114]
        entry.C001036 = temp[115]
        entry.C001037 = temp[116]
        entry.C001038 = temp[117]
        entry.C001045 = temp[118]
        entry.C001046 = temp[119]
        entry.C001047 = temp[120]
        entry.C001048 = temp[121]
        entry.C001049 = temp[122]
        entry.C001050 = temp[123]
        entry.C001051 = temp[124]
        entry.C001053 = temp[125]
        entry.C001056 = temp[126]
        entry.C001058 = temp[127]
        entry.C001059 = temp[128]
        entry.C001060 = temp[129]
        entry.C001061 = temp[130]
        entry.C001062 = temp[131]
        entry.C001063 = temp[132]
        entry.C001064 = temp[133]
        entry.C001066 = temp[134]
        entry.C001067 = temp[135]
        entry.C001068 = temp[136]
        entry.C001069 = temp[137]
        entry.C001070 = temp[138]
        entry.C001071 = temp[139]
        entry.C001072 = temp[140]
        entry.C001075 = temp[141]
        entry.C001076 = temp[142]
        entry.C001077 = temp[143]
        entry.C001078 = temp[144]
        entry.C001080 = temp[145]
        entry.C001081 = temp[146]
        entry.C001082 = temp[147]
        entry.C001083 = temp[148]
        entry.C001084 = temp[149]
        entry.C001085 = temp[150]
        entry.C001086 = temp[151]
        entry.C001087 = temp[152]
        entry.C001088 = temp[153]
        entry.C001089 = temp[154]
        entry.C001090 = temp[155]
        entry.C001091 = temp[156]
        entry.C001092 = temp[157]
        entry.C001093 = temp[158]
        entry.C001094 = temp[159]
        entry.C001095 = temp[160]
        entry.C001096 = temp[161]
        entry.C001097 = temp[162]
        entry.C001098 = temp[163]
        entry.C001101 = temp[164]
        entry.C001102 = temp[165]
        entry.C001103 = temp[166]
        entry.C001105 = temp[167]
        entry.C001106 = temp[168]
        entry.C001107 = temp[169]
        entry.D000096 = temp[170]
        entry.D000191 = temp[171]
        entry.D000197 = temp[172]
        entry.D000216 = temp[173]
        entry.D000327 = temp[174]
        entry.D000355 = temp[175]
        entry.D000399 = temp[176]
        entry.D000482 = temp[177]
        entry.D000492 = temp[178]
        entry.D000533 = temp[179]
        entry.D000563 = temp[180]
        entry.D000595 = temp[181]
        entry.D000598 = temp[182]
        entry.D000600 = temp[183]
        entry.D000604 = temp[184]
        entry.D000607 = temp[185]
        entry.D000610 = temp[186]
        entry.D000612 = temp[187]
        entry.D000613 = temp[188]
        entry.D000614 = temp[189]
        entry.D000615 = temp[190]
        entry.D000616 = temp[191]
        entry.D000617 = temp[192]
        entry.D000618 = temp[193]
        entry.D000619 = temp[194]
        entry.D000620 = temp[195]
        entry.D000621 = temp[196]
        entry.D000622 = temp[197]
        entry.D000623 = temp[198]
        entry.D000624 = temp[199]
        entry.D000625 = temp[200]
        entry.E000172 = temp[201]
        entry.E000179 = temp[202]
        entry.E000215 = temp[203]
        entry.E000285 = temp[204]
        entry.E000288 = temp[205]
        entry.E000290 = temp[206]
        entry.E000291 = temp[207]
        entry.E000292 = temp[208]
        entry.E000293 = temp[209]
        entry.E000294 = temp[210]
        entry.E000295 = temp[211]
        entry.F000010 = temp[212]
        entry.F000030 = temp[213]
        entry.F000043 = temp[214]
        entry.F000062 = temp[215]
        entry.F000116 = temp[216]
        entry.F000339 = temp[217]
        entry.F000372 = temp[218]
        entry.F000444 = temp[219]
        entry.F000445 = temp[220]
        entry.F000448 = temp[221]
        entry.F000449 = temp[222]
        entry.F000450 = temp[223]
        entry.F000451 = temp[224]
        entry.F000454 = temp[225]
        entry.F000455 = temp[226]
        entry.F000456 = temp[227]
        entry.F000457 = temp[228]
        entry.F000458 = temp[229]
        entry.F000459 = temp[230]
        entry.F000460 = temp[231]
        entry.F000461 = temp[232]
        entry.F000462 = temp[233]
        entry.F000463 = temp[234]
        entry.G000021 = temp[235]
        entry.G000289 = temp[236]
        entry.G000359 = temp[237]
        entry.G000377 = temp[238]
        entry.G000386 = temp[239]
        entry.G000410 = temp[240]
        entry.G000535 = temp[241]
        entry.G000544 = temp[242]
        entry.G000546 = temp[243]
        entry.G000548 = temp[244]
        entry.G000549 = temp[245]
        entry.G000550 = temp[246]
        entry.G000551 = temp[247]
        entry.G000552 = temp[248]
        entry.G000553 = temp[249]
        entry.G000555 = temp[250]
        entry.G000556 = temp[251]
        entry.G000558 = temp[252]
        entry.G000559 = temp[253]
        entry.G000560 = temp[254]
        entry.G000562 = temp[255]
        entry.G000563 = temp[256]
        entry.G000564 = temp[257]
        entry.G000565 = temp[258]
        entry.G000566 = temp[259]
        entry.G000567 = temp[260]
        entry.G000568 = temp[261]
        entry.G000569 = temp[262]
        entry.G000570 = temp[263]
        entry.G000571 = temp[264]
        entry.G000572 = temp[265]
        entry.G000573 = temp[266]
        entry.G000574 = temp[267]
        entry.G000575 = temp[268]
        entry.G000576 = temp[269]
        entry.G000577 = temp[270]
        entry.H000067 = temp[271]
        entry.H000206 = temp[272]
        entry.H000324 = temp[273]
        entry.H000329 = temp[274]
        entry.H000338 = temp[275]
        entry.H000528 = temp[276]
        entry.H000627 = temp[277]
        entry.H000636 = temp[278]
        entry.H000712 = temp[279]
        entry.H000874 = temp[280]
        entry.H001016 = temp[281]
        entry.H001032 = temp[282]
        entry.H001034 = temp[283]
        entry.H001036 = temp[284]
        entry.H001038 = temp[285]
        entry.H001041 = temp[286]
        entry.H001042 = temp[287]
        entry.H001045 = temp[288]
        entry.H001046 = temp[289]
        entry.H001047 = temp[290]
        entry.H001048 = temp[291]
        entry.H001049 = temp[292]
        entry.H001050 = temp[293]
        entry.H001051 = temp[294]
        entry.H001052 = temp[295]
        entry.H001053 = temp[296]
        entry.H001054 = temp[297]
        entry.H001055 = temp[298]
        entry.H001056 = temp[299]
        entry.H001057 = temp[300]
        entry.H001058 = temp[301]
        entry.H001059 = temp[302]
        entry.H001060 = temp[303]
        entry.H001061 = temp[304]
        entry.H001062 = temp[305]
        entry.H001063 = temp[306]
        entry.H001064 = temp[307]
        entry.H001065 = temp[308]
        entry.H001066 = temp[309]
        entry.H001067 = temp[310]
        entry.H001068 = temp[311]
        entry.H001069 = temp[312]
        entry.H001070 = temp[313]
        entry.H001071 = temp[314]
        entry.H001072 = temp[315]
        entry.H001073 = temp[316]
        entry.I000024 = temp[317]
        entry.I000055 = temp[318]
        entry.I000056 = temp[319]
        entry.I000057 = temp[320]
        entry.J000032 = temp[321]
        entry.J000126 = temp[322]
        entry.J000174 = temp[323]
        entry.J000177 = temp[324]
        entry.J000255 = temp[325]
        entry.J000283 = temp[326]
        entry.J000285 = temp[327]
        entry.J000288 = temp[328]
        entry.J000289 = temp[329]
        entry.J000290 = temp[330]
        entry.J000291 = temp[331]
        entry.J000292 = temp[332]
        entry.J000293 = temp[333]
        entry.J000294 = temp[334]
        entry.J000295 = temp[335]
        entry.J000296 = temp[336]
        entry.J000297 = temp[337]
        entry.K000009 = temp[338]
        entry.K000148 = temp[339]
        entry.K000172 = temp[340]
        entry.K000188 = temp[341]
        entry.K000210 = temp[342]
        entry.K000220 = temp[343]
        entry.K000305 = temp[344]
        entry.K000336 = temp[345]
        entry.K000352 = temp[346]
        entry.K000360 = temp[347]
        entry.K000362 = temp[348]
        entry.K000363 = temp[349]
        entry.K000367 = temp[350]
        entry.K000368 = temp[351]
        entry.K000369 = temp[352]
        entry.K000375 = temp[353]
        entry.K000376 = temp[354]
        entry.K000378 = temp[355]
        entry.K000379 = temp[356]
        entry.K000380 = temp[357]
        entry.K000381 = temp[358]
        entry.K000382 = temp[359]
        entry.K000383 = temp[360]
        entry.K000384 = temp[361]
        entry.K000385 = temp[362]
        entry.K000386 = temp[363]
        entry.K000387 = temp[364]
        entry.K000388 = temp[365]
        entry.L000111 = temp[366]
        entry.L000123 = temp[367]
        entry.L000174 = temp[368]
        entry.L000261 = temp[369]
        entry.L000263 = temp[370]
        entry.L000274 = temp[371]
        entry.L000287 = temp[372]
        entry.L000304 = temp[373]
        entry.L000397 = temp[374]
        entry.L000480 = temp[375]
        entry.L000491 = temp[376]
        entry.L000504 = temp[377]
        entry.L000517 = temp[378]
        entry.L000550 = temp[379]
        entry.L000551 = temp[380]
        entry.L000553 = temp[381]
        entry.L000554 = temp[382]
        entry.L000557 = temp[383]
        entry.L000559 = temp[384]
        entry.L000560 = temp[385]
        entry.L000562 = temp[386]
        entry.L000563 = temp[387]
        entry.L000564 = temp[388]
        entry.L000565 = temp[389]
        entry.L000566 = temp[390]
        entry.L000567 = temp[391]
        entry.L000569 = temp[392]
        entry.L000570 = temp[393]
        entry.L000571 = temp[394]
        entry.L000573 = temp[395]
        entry.L000574 = temp[396]
        entry.L000575 = temp[397]
        entry.L000576 = temp[398]
        entry.L000577 = temp[399]
        entry.L000578 = temp[400]
        entry.L000579 = temp[401]
        entry.L000580 = temp[402]
        entry.L000581 = temp[403]
        entry.L000582 = temp[404]
        entry.L000583 = temp[405]
        entry.L000584 = temp[406]
        entry.L000585 = temp[407]
        entry.M000087 = temp[408]
        entry.M000133 = temp[409]
        entry.M000303 = temp[410]
        entry.M000309 = temp[411]
        entry.M000312 = temp[412]
        entry.M000355 = temp[413]
        entry.M000404 = temp[414]
        entry.M000485 = temp[415]
        entry.M000508 = temp[416]
        entry.M000639 = temp[417]
        entry.M000689 = temp[418]
        entry.M000702 = temp[419]
        entry.M000725 = temp[420]
        entry.M000933 = temp[421]
        entry.M000934 = temp[422]
        entry.M001111 = temp[423]
        entry.M001134 = temp[424]
        entry.M001137 = temp[425]
        entry.M001138 = temp[426]
        entry.M001139 = temp[427]
        entry.M001142 = temp[428]
        entry.M001143 = temp[429]
        entry.M001144 = temp[430]
        entry.M001149 = temp[431]
        entry.M001150 = temp[432]
        entry.M001151 = temp[433]
        entry.M001153 = temp[434]
        entry.M001154 = temp[435]
        entry.M001155 = temp[436]
        entry.M001156 = temp[437]
        entry.M001157 = temp[438]
        entry.M001158 = temp[439]
        entry.M001159 = temp[440]
        entry.M001160 = temp[441]
        entry.M001163 = temp[442]
        entry.M001165 = temp[443]
        entry.M001166 = temp[444]
        entry.M001169 = temp[445]
        entry.M001170 = temp[446]
        entry.M001171 = temp[447]
        entry.M001176 = temp[448]
        entry.M001177 = temp[449]
        entry.M001179 = temp[450]
        entry.M001180 = temp[451]
        entry.M001181 = temp[452]
        entry.M001182 = temp[453]
        entry.M001183 = temp[454]
        entry.M001184 = temp[455]
        entry.M001185 = temp[456]
        entry.M001187 = temp[457]
        entry.M001188 = temp[458]
        entry.M001189 = temp[459]
        entry.M001190 = temp[460]
        entry.M001191 = temp[461]
        entry.M001192 = temp[462]
        entry.M001193 = temp[463]
        entry.M001194 = temp[464]
        entry.M001195 = temp[465]
        entry.M001196 = temp[466]
        entry.M001197 = temp[467]
        entry.N000002 = temp[468]
        entry.N000015 = temp[469]
        entry.N000032 = temp[470]
        entry.N000127 = temp[471]
        entry.N000147 = temp[472]
        entry.N000179 = temp[473]
        entry.N000180 = temp[474]
        entry.N000181 = temp[475]
        entry.N000182 = temp[476]
        entry.N000184 = temp[477]
        entry.N000185 = temp[478]
        entry.N000186 = temp[479]
        entry.N000187 = temp[480]
        entry.N000188 = temp[481]
        entry.N000189 = temp[482]
        entry.O000085 = temp[483]
        entry.O000168 = temp[484]
        entry.O000169 = temp[485]
        entry.O000170 = temp[486]
        entry.P000034 = temp[487]
        entry.P000096 = temp[488]
        entry.P000099 = temp[489]
        entry.P000197 = temp[490]
        entry.P000258 = temp[491]
        entry.P000265 = temp[492]
        entry.P000373 = temp[493]
        entry.P000449 = temp[494]
        entry.P000523 = temp[495]
        entry.P000583 = temp[496]
        entry.P000585 = temp[497]
        entry.P000587 = temp[498]
        entry.P000588 = temp[499]
        entry.P000590 = temp[500]
        entry.P000591 = temp[501]
        entry.P000592 = temp[502]
        entry.P000593 = temp[503]
        entry.P000594 = temp[504]
        entry.P000595 = temp[505]
        entry.P000596 = temp[506]
        entry.P000597 = temp[507]
        entry.P000598 = temp[508]
        entry.P000599 = temp[509]
        entry.P000601 = temp[510]
        entry.P000602 = temp[511]
        entry.P000603 = temp[512]
        entry.P000604 = temp[513]
        entry.P000605 = temp[514]
        entry.P000606 = temp[515]
        entry.P000607 = temp[516]
        entry.P000608 = temp[517]
        entry.P000609 = temp[518]
        entry.P000610 = temp[519]
        entry.P000611 = temp[520]
        entry.P000612 = temp[521]
        entry.Q000023 = temp[522]
        entry.Q000024 = temp[523]
        entry.R000011 = temp[524]
        entry.R000053 = temp[525]
        entry.R000122 = temp[526]
        entry.R000146 = temp[527]
        entry.R000170 = temp[528]
        entry.R000307 = temp[529]
        entry.R000361 = temp[530]
        entry.R000395 = temp[531]
        entry.R000409 = temp[532]
        entry.R000435 = temp[533]
        entry.R000462 = temp[534]
        entry.R000486 = temp[535]
        entry.R000487 = temp[536]
        entry.R000515 = temp[537]
        entry.R000570 = temp[538]
        entry.R000571 = temp[539]
        entry.R000572 = temp[540]
        entry.R000573 = temp[541]
        entry.R000575 = temp[542]
        entry.R000576 = temp[543]
        entry.R000577 = temp[544]
        entry.R000578 = temp[545]
        entry.R000580 = temp[546]
        entry.R000581 = temp[547]
        entry.R000582 = temp[548]
        entry.R000583 = temp[549]
        entry.R000584 = temp[550]
        entry.R000585 = temp[551]
        entry.R000586 = temp[552]
        entry.R000587 = temp[553]
        entry.R000588 = temp[554]
        entry.R000589 = temp[555]
        entry.R000590 = temp[556]
        entry.R000591 = temp[557]
        entry.R000592 = temp[558]
        entry.R000593 = temp[559]
        entry.R000594 = temp[560]
        entry.R000595 = temp[561]
        entry.R000597 = temp[562]
        entry.R000598 = temp[563]
        entry.R000599 = temp[564]
        entry.R000600 = temp[565]
        entry.R000601 = temp[566]
        entry.R000602 = temp[567]
        entry.R000603 = temp[568]
        entry.R000604 = temp[569]
        entry.R000605 = temp[570]
        entry.S000018 = temp[571]
        entry.S000030 = temp[572]
        entry.S000033 = temp[573]
        entry.S000051 = temp[574]
        entry.S000148 = temp[575]
        entry.S000185 = temp[576]
        entry.S000244 = temp[577]
        entry.S000248 = temp[578]
        entry.S000250 = temp[579]
        entry.S000320 = temp[580]
        entry.S000344 = temp[581]
        entry.S000364 = temp[582]
        entry.S000480 = temp[583]
        entry.S000510 = temp[584]
        entry.S000522 = temp[585]
        entry.S000583 = temp[586]
        entry.S000663 = temp[587]
        entry.S000770 = temp[588]
        entry.S000810 = temp[589]
        entry.S000822 = temp[590]
        entry.S000937 = temp[591]
        entry.S001141 = temp[592]
        entry.S001145 = temp[593]
        entry.S001148 = temp[594]
        entry.S001150 = temp[595]
        entry.S001154 = temp[596]
        entry.S001155 = temp[597]
        entry.S001156 = temp[598]
        entry.S001157 = temp[599]
        entry.S001162 = temp[600]
        entry.S001164 = temp[601]
        entry.S001165 = temp[602]
        entry.S001168 = temp[603]
        entry.S001170 = temp[604]
        entry.S001171 = temp[605]
        entry.S001172 = temp[606]
        entry.S001174 = temp[607]
        entry.S001175 = temp[608]
        entry.S001176 = temp[609]
        entry.S001177 = temp[610]
        entry.S001179 = temp[611]
        entry.S001180 = temp[612]
        entry.S001181 = temp[613]
        entry.S001182 = temp[614]
        entry.S001183 = temp[615]
        entry.S001184 = temp[616]
        entry.S001185 = temp[617]
        entry.S001186 = temp[618]
        entry.S001187 = temp[619]
        entry.S001188 = temp[620]
        entry.S001189 = temp[621]
        entry.S001190 = temp[622]
        entry.S001191 = temp[623]
        entry.S001192 = temp[624]
        entry.S001193 = temp[625]
        entry.S001194 = temp[626]
        entry.S001195 = temp[627]
        entry.S001196 = temp[628]
        entry.S001197 = temp[629]
        entry.S001198 = temp[630]
        entry.T000193 = temp[631]
        entry.T000238 = temp[632]
        entry.T000250 = temp[633]
        entry.T000266 = temp[634]
        entry.T000326 = temp[635]
        entry.T000459 = temp[636]
        entry.T000460 = temp[637]
        entry.T000461 = temp[638]
        entry.T000462 = temp[639]
        entry.T000463 = temp[640]
        entry.T000464 = temp[641]
        entry.T000465 = temp[642]
        entry.T000467 = temp[643]
        entry.T000468 = temp[644]
        entry.T000469 = temp[645]
        entry.T000470 = temp[646]
        entry.T000471 = temp[647]
        entry.T000472 = temp[648]
        entry.T000473 = temp[649]
        entry.T000474 = temp[650]
        entry.T000475 = temp[651]
        entry.T000476 = temp[652]
        entry.U000031 = temp[653]
        entry.U000038 = temp[654]
        entry.U000039 = temp[655]
        entry.V000081 = temp[656]
        entry.V000108 = temp[657]
        entry.V000127 = temp[658]
        entry.V000128 = temp[659]
        entry.V000129 = temp[660]
        entry.V000130 = temp[661]
        entry.V000131 = temp[662]
        entry.V000132 = temp[663]
        entry.W000187 = temp[664]
        entry.W000207 = temp[665]
        entry.W000215 = temp[666]
        entry.W000413 = temp[667]
        entry.W000437 = temp[668]
        entry.W000672 = temp[669]
        entry.W000738 = temp[670]
        entry.W000779 = temp[671]
        entry.W000791 = temp[672]
        entry.W000795 = temp[673]
        entry.W000796 = temp[674]
        entry.W000797 = temp[675]
        entry.W000798 = temp[676]
        entry.W000799 = temp[677]
        entry.W000800 = temp[678]
        entry.W000802 = temp[679]
        entry.W000803 = temp[680]
        entry.W000804 = temp[681]
        entry.W000805 = temp[682]
        entry.W000806 = temp[683]
        entry.W000807 = temp[684]
        entry.W000808 = temp[685]
        entry.W000809 = temp[686]
        entry.W000810 = temp[687]
        entry.W000811 = temp[688]
        entry.W000812 = temp[689]
        entry.W000813 = temp[690]
        entry.W000814 = temp[691]
        entry.W000815 = temp[692]
        entry.W000816 = temp[693]
        entry.W000817 = temp[694]
        entry.W000818 = temp[695]
        entry.W000819 = temp[696]
        entry.W000820 = temp[697]
        entry.W000821 = temp[698]
        entry.W000822 = temp[699]
        entry.Y000031 = temp[700]
        entry.Y000033 = temp[701]
        entry.Y000062 = temp[702]
        entry.Y000063 = temp[703]
        entry.Y000064 = temp[704]
        entry.Y000065 = temp[705]
        entry.Y000066 = temp[706]
        entry.Z000017 = temp[707]
        entry.Z000018 = temp[708]
        entry.put()

def process_nationalpolls(blob_info, party):
    logging.error('THE FUNCTION RUNS')
    logging.error(party)
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        if party == 'D':
            d = row_str.split(',')
            a = d[3].split(' UTC')
            startupdate = datetime.strptime(d[1], '%Y-%m-%d')
            endupdate = datetime.strptime(d[2], '%Y-%m-%d')
            update = datetime.strptime(a[0], '%Y-%m-%d %H:%M:%S')
            entry = NationalDemocraticPrimary(pollster=d[0], start_date=startupdate, end_date=endupdate, entry_date=update, popsize=int(d[4]), poptype=d[5], mode=d[6], hill=int(d[7]), sanders=int(d[8]), omalley=int(d[9]), biden=int(d[10]), chafee=int(d[11]), lessig=int(d[12]), webb=int(d[13]), undecided=int(d[14]), url=d[15])
            entry.put()
        if party == 'R':
            d = row_str.split(',')
            a = d[3].split(' UTC')
            startupdate = datetime.strptime(d[1], '%Y-%m-%d')
            endupdate = datetime.strptime(d[2], '%Y-%m-%d')
            update = datetime.strptime(a[0], '%Y-%m-%d %H:%M:%S')
            entry = NationalRepublicanPrimary(pollster=d[0], start_date=startupdate, end_date=endupdate, entry_date=update, popsize=int(d[4]), poptype=d[5],mode=d[6],trump=int(d[7]),cruz=int(d[8]),rubio=int(d[9]),carson=int(d[10]),bush=int(d[11]),christie=int(d[12]),paul=int(d[13]),fiorina=int(d[14]),huckabee=int(d[15]),kasich=int(d[16]),santorum=int(d[17]),gilmore=int(d[18]),gram=int(d[19]),jindal=int(d[20]),pataki=int(d[21]),perry=int(d[22]),walker=int(d[23]),undecided=int(d[24]),url=d[25])
            entry.put()
