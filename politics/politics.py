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
from google.appengine.ext.webapp.util import run_wsgi_app
from datetime import datetime, date, time

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.db import GqlQuery
from google.appengine.api import mail


#from oauth2client.client import flow_from_clientsecrets
#from oauth2client.client import FlowExchangeError
#import httplib2
#import requests


#logging.error('my string')

login_session = {}

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = '2A3437B9B29034B7'
sunlight_key = '5a2e18d2e3ed4861a8604e9a5f96a47a'


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
#---------------------------Input Validation Functions----------------------------
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return email and EMAIL_RE.match(email)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

ZIP_RE = re.compile(r'^[0-9]{5}(?:-[0-9]{4})?$')
def valid_zip(zip):
    return zip and ZIP_RE.match(zip)

DISTRICT_RE = re.compile(r'^[A-Z]{2}[:]{1}[1-9]{1}')
def valid_district(district):
    return district and DISTRICT_RE.match(district)

#---------------------------User Implementation Functions--------------------------
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(username, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(username + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

#------------------------File Processing----------------------------

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
        if (count%25 == 0):
            break

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
#-------------------------Database Classes------------------------------
class User(db.Model):
    username = db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    district = db.StringProperty()
    age = db.IntegerProperty()
    gender = db.StringProperty()
    created = db.DateTimeProperty(required = True, auto_now = True)
    last_modified = db.DateTimeProperty(required = True, auto_now = True)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_email(cls, email):
        u = cls.all().filter('email =', email).get()
        return u

    @classmethod
    def by_username(cls, username):
        u = cls.all().filter('username =', username).get()
        return u

    @classmethod
    def register(cls, username, email, pw):
        pw_hash = make_pw_hash(username, pw)
        return cls( username = username,
                    email = email,
                    pw_hash = pw_hash)

    @classmethod
    def login(cls, username, pw):
        u = cls.by_username(username)
        if u and valid_pw(username, pw, u.pw_hash):
            return u

class Votes(db.Model):
    bill_id = db.StringProperty(required = True)
    rid = db.StringProperty(required = True)
    congress = db.StringProperty(required = True)
    voted_at = db.StringProperty(required = True)
    vote_type = db.StringProperty(required = True)
    roll_type = db.StringProperty(required = True)
    question = db.StringProperty(required = True)
    required = db.StringProperty(required = True)
    result = db.StringProperty(required = True)
    source = db.StringProperty(required = True)
    breakdown = db.StringProperty(required = True)
    break_gop = db.StringProperty(required = True)
    break_dem = db.StringProperty(required = True)
    break_ind = db.StringProperty(required = True)

class Ind_Votes(db.Model):
    bill_id = db.StringProperty(required = True)
    roll_id = db.StringProperty(required = True)
    A000022 = db.StringProperty(required = False)
    A000055 = db.StringProperty(required = False)
    A000069 = db.StringProperty(required = False)
    A000210 = db.StringProperty(required = False)
    A000358 = db.StringProperty(required = False)
    A000360 = db.StringProperty(required = False)
    A000361 = db.StringProperty(required = False)
    A000362 = db.StringProperty(required = False)
    A000365 = db.StringProperty(required = False)
    A000366 = db.StringProperty(required = False)
    A000367 = db.StringProperty(required = False)
    A000368 = db.StringProperty(required = False)
    A000369 = db.StringProperty(required = False)
    A000370 = db.StringProperty(required = False)
    A000371 = db.StringProperty(required = False)
    A000372 = db.StringProperty(required = False)
    A000373 = db.StringProperty(required = False)
    A000374 = db.StringProperty(required = False)
    B000013 = db.StringProperty(required = False)
    B000208 = db.StringProperty(required = False)
    B000213 = db.StringProperty(required = False)
    B000220 = db.StringProperty(required = False)
    B000243 = db.StringProperty(required = False)
    B000287 = db.StringProperty(required = False)
    B000410 = db.StringProperty(required = False)
    B000461 = db.StringProperty(required = False)
    B000468 = db.StringProperty(required = False)
    B000490 = db.StringProperty(required = False)
    B000574 = db.StringProperty(required = False)
    B000575 = db.StringProperty(required = False)
    B000589 = db.StringProperty(required = False)
    B000652 = db.StringProperty(required = False)
    B000711 = db.StringProperty(required = False)
    B000755 = db.StringProperty(required = False)
    B000911 = db.StringProperty(required = False)
    B000944 = db.StringProperty(required = False)
    B001135 = db.StringProperty(required = False)
    B001149 = db.StringProperty(required = False)
    B001227 = db.StringProperty(required = False)
    B001228 = db.StringProperty(required = False)
    B001230 = db.StringProperty(required = False)
    B001231 = db.StringProperty(required = False)
    B001232 = db.StringProperty(required = False)
    B001234 = db.StringProperty(required = False)
    B001236 = db.StringProperty(required = False)
    B001242 = db.StringProperty(required = False)
    B001243 = db.StringProperty(required = False)
    B001244 = db.StringProperty(required = False)
    B001245 = db.StringProperty(required = False)
    B001248 = db.StringProperty(required = False)
    B001250 = db.StringProperty(required = False)
    B001251 = db.StringProperty(required = False)
    B001252 = db.StringProperty(required = False)
    B001254 = db.StringProperty(required = False)
    B001255 = db.StringProperty(required = False)
    B001256 = db.StringProperty(required = False)
    B001257 = db.StringProperty(required = False)
    B001259 = db.StringProperty(required = False)
    B001260 = db.StringProperty(required = False)
    B001261 = db.StringProperty(required = False)
    B001262 = db.StringProperty(required = False)
    B001265 = db.StringProperty(required = False)
    B001267 = db.StringProperty(required = False)
    B001268 = db.StringProperty(required = False)
    B001269 = db.StringProperty(required = False)
    B001270 = db.StringProperty(required = False)
    B001271 = db.StringProperty(required = False)
    B001272 = db.StringProperty(required = False)
    B001273 = db.StringProperty(required = False)
    B001274 = db.StringProperty(required = False)
    B001275 = db.StringProperty(required = False)
    B001276 = db.StringProperty(required = False)
    B001277 = db.StringProperty(required = False)
    B001278 = db.StringProperty(required = False)
    B001279 = db.StringProperty(required = False)
    B001280 = db.StringProperty(required = False)
    B001281 = db.StringProperty(required = False)
    B001282 = db.StringProperty(required = False)
    B001283 = db.StringProperty(required = False)
    B001284 = db.StringProperty(required = False)
    B001285 = db.StringProperty(required = False)
    B001286 = db.StringProperty(required = False)
    B001287 = db.StringProperty(required = False)
    B001288 = db.StringProperty(required = False)
    B001289 = db.StringProperty(required = False)
    B001290 = db.StringProperty(required = False)
    B001291 = db.StringProperty(required = False)
    B001292 = db.StringProperty(required = False)
    B001293 = db.StringProperty(required = False)
    B001294 = db.StringProperty(required = False)
    B001295 = db.StringProperty(required = False)
    B001296 = db.StringProperty(required = False)
    B001297 = db.StringProperty(required = False)
    C000059 = db.StringProperty(required = False)
    C000071 = db.StringProperty(required = False)
    C000127 = db.StringProperty(required = False)
    C000141 = db.StringProperty(required = False)
    C000174 = db.StringProperty(required = False)
    C000266 = db.StringProperty(required = False)
    C000286 = db.StringProperty(required = False)
    C000380 = db.StringProperty(required = False)
    C000537 = db.StringProperty(required = False)
    C000542 = db.StringProperty(required = False)
    C000556 = db.StringProperty(required = False)
    C000560 = db.StringProperty(required = False)
    C000567 = db.StringProperty(required = False)
    C000705 = db.StringProperty(required = False)
    C000714 = db.StringProperty(required = False)
    C000754 = db.StringProperty(required = False)
    C000794 = db.StringProperty(required = False)
    C000880 = db.StringProperty(required = False)
    C000984 = db.StringProperty(required = False)
    C001035 = db.StringProperty(required = False)
    C001036 = db.StringProperty(required = False)
    C001037 = db.StringProperty(required = False)
    C001038 = db.StringProperty(required = False)
    C001045 = db.StringProperty(required = False)
    C001046 = db.StringProperty(required = False)
    C001047 = db.StringProperty(required = False)
    C001048 = db.StringProperty(required = False)
    C001049 = db.StringProperty(required = False)
    C001050 = db.StringProperty(required = False)
    C001051 = db.StringProperty(required = False)
    C001053 = db.StringProperty(required = False)
    C001056 = db.StringProperty(required = False)
    C001058 = db.StringProperty(required = False)
    C001059 = db.StringProperty(required = False)
    C001060 = db.StringProperty(required = False)
    C001061 = db.StringProperty(required = False)
    C001062 = db.StringProperty(required = False)
    C001063 = db.StringProperty(required = False)
    C001064 = db.StringProperty(required = False)
    C001066 = db.StringProperty(required = False)
    C001067 = db.StringProperty(required = False)
    C001068 = db.StringProperty(required = False)
    C001069 = db.StringProperty(required = False)
    C001070 = db.StringProperty(required = False)
    C001071 = db.StringProperty(required = False)
    C001072 = db.StringProperty(required = False)
    C001075 = db.StringProperty(required = False)
    C001076 = db.StringProperty(required = False)
    C001077 = db.StringProperty(required = False)
    C001078 = db.StringProperty(required = False)
    C001080 = db.StringProperty(required = False)
    C001081 = db.StringProperty(required = False)
    C001082 = db.StringProperty(required = False)
    C001083 = db.StringProperty(required = False)
    C001084 = db.StringProperty(required = False)
    C001085 = db.StringProperty(required = False)
    C001086 = db.StringProperty(required = False)
    C001087 = db.StringProperty(required = False)
    C001088 = db.StringProperty(required = False)
    C001089 = db.StringProperty(required = False)
    C001090 = db.StringProperty(required = False)
    C001091 = db.StringProperty(required = False)
    C001092 = db.StringProperty(required = False)
    C001093 = db.StringProperty(required = False)
    C001094 = db.StringProperty(required = False)
    C001095 = db.StringProperty(required = False)
    C001096 = db.StringProperty(required = False)
    C001097 = db.StringProperty(required = False)
    C001098 = db.StringProperty(required = False)
    C001101 = db.StringProperty(required = False)
    C001102 = db.StringProperty(required = False)
    C001103 = db.StringProperty(required = False)
    C001105 = db.StringProperty(required = False)
    C001106 = db.StringProperty(required = False)
    C001107 = db.StringProperty(required = False)
    D000096 = db.StringProperty(required = False)
    D000191 = db.StringProperty(required = False)
    D000197 = db.StringProperty(required = False)
    D000216 = db.StringProperty(required = False)
    D000327 = db.StringProperty(required = False)
    D000355 = db.StringProperty(required = False)
    D000399 = db.StringProperty(required = False)
    D000482 = db.StringProperty(required = False)
    D000492 = db.StringProperty(required = False)
    D000533 = db.StringProperty(required = False)
    D000563 = db.StringProperty(required = False)
    D000595 = db.StringProperty(required = False)
    D000598 = db.StringProperty(required = False)
    D000600 = db.StringProperty(required = False)
    D000604 = db.StringProperty(required = False)
    D000607 = db.StringProperty(required = False)
    D000610 = db.StringProperty(required = False)
    D000612 = db.StringProperty(required = False)
    D000613 = db.StringProperty(required = False)
    D000614 = db.StringProperty(required = False)
    D000615 = db.StringProperty(required = False)
    D000616 = db.StringProperty(required = False)
    D000617 = db.StringProperty(required = False)
    D000618 = db.StringProperty(required = False)
    D000619 = db.StringProperty(required = False)
    D000620 = db.StringProperty(required = False)
    D000621 = db.StringProperty(required = False)
    D000622 = db.StringProperty(required = False)
    D000623 = db.StringProperty(required = False)
    D000624 = db.StringProperty(required = False)
    D000625 = db.StringProperty(required = False)
    E000172 = db.StringProperty(required = False)
    E000179 = db.StringProperty(required = False)
    E000215 = db.StringProperty(required = False)
    E000285 = db.StringProperty(required = False)
    E000288 = db.StringProperty(required = False)
    E000290 = db.StringProperty(required = False)
    E000291 = db.StringProperty(required = False)
    E000292 = db.StringProperty(required = False)
    E000293 = db.StringProperty(required = False)
    E000294 = db.StringProperty(required = False)
    E000295 = db.StringProperty(required = False)
    F000010 = db.StringProperty(required = False)
    F000030 = db.StringProperty(required = False)
    F000043 = db.StringProperty(required = False)
    F000062 = db.StringProperty(required = False)
    F000116 = db.StringProperty(required = False)
    F000339 = db.StringProperty(required = False)
    F000372 = db.StringProperty(required = False)
    F000444 = db.StringProperty(required = False)
    F000445 = db.StringProperty(required = False)
    F000448 = db.StringProperty(required = False)
    F000449 = db.StringProperty(required = False)
    F000450 = db.StringProperty(required = False)
    F000451 = db.StringProperty(required = False)
    F000454 = db.StringProperty(required = False)
    F000455 = db.StringProperty(required = False)
    F000456 = db.StringProperty(required = False)
    F000457 = db.StringProperty(required = False)
    F000458 = db.StringProperty(required = False)
    F000459 = db.StringProperty(required = False)
    F000460 = db.StringProperty(required = False)
    F000461 = db.StringProperty(required = False)
    F000462 = db.StringProperty(required = False)
    F000463 = db.StringProperty(required = False)
    G000021 = db.StringProperty(required = False)
    G000289 = db.StringProperty(required = False)
    G000359 = db.StringProperty(required = False)
    G000377 = db.StringProperty(required = False)
    G000386 = db.StringProperty(required = False)
    G000410 = db.StringProperty(required = False)
    G000535 = db.StringProperty(required = False)
    G000544 = db.StringProperty(required = False)
    G000546 = db.StringProperty(required = False)
    G000548 = db.StringProperty(required = False)
    G000549 = db.StringProperty(required = False)
    G000550 = db.StringProperty(required = False)
    G000551 = db.StringProperty(required = False)
    G000552 = db.StringProperty(required = False)
    G000553 = db.StringProperty(required = False)
    G000555 = db.StringProperty(required = False)
    G000556 = db.StringProperty(required = False)
    G000558 = db.StringProperty(required = False)
    G000559 = db.StringProperty(required = False)
    G000560 = db.StringProperty(required = False)
    G000562 = db.StringProperty(required = False)
    G000563 = db.StringProperty(required = False)
    G000564 = db.StringProperty(required = False)
    G000565 = db.StringProperty(required = False)
    G000566 = db.StringProperty(required = False)
    G000567 = db.StringProperty(required = False)
    G000568 = db.StringProperty(required = False)
    G000569 = db.StringProperty(required = False)
    G000570 = db.StringProperty(required = False)
    G000571 = db.StringProperty(required = False)
    G000572 = db.StringProperty(required = False)
    G000573 = db.StringProperty(required = False)
    G000574 = db.StringProperty(required = False)
    G000575 = db.StringProperty(required = False)
    G000576 = db.StringProperty(required = False)
    G000577 = db.StringProperty(required = False)
    H000067 = db.StringProperty(required = False)
    H000206 = db.StringProperty(required = False)
    H000324 = db.StringProperty(required = False)
    H000329 = db.StringProperty(required = False)
    H000338 = db.StringProperty(required = False)
    H000528 = db.StringProperty(required = False)
    H000627 = db.StringProperty(required = False)
    H000636 = db.StringProperty(required = False)
    H000712 = db.StringProperty(required = False)
    H000874 = db.StringProperty(required = False)
    H001016 = db.StringProperty(required = False)
    H001032 = db.StringProperty(required = False)
    H001034 = db.StringProperty(required = False)
    H001036 = db.StringProperty(required = False)
    H001038 = db.StringProperty(required = False)
    H001041 = db.StringProperty(required = False)
    H001042 = db.StringProperty(required = False)
    H001045 = db.StringProperty(required = False)
    H001046 = db.StringProperty(required = False)
    H001047 = db.StringProperty(required = False)
    H001048 = db.StringProperty(required = False)
    H001049 = db.StringProperty(required = False)
    H001050 = db.StringProperty(required = False)
    H001051 = db.StringProperty(required = False)
    H001052 = db.StringProperty(required = False)
    H001053 = db.StringProperty(required = False)
    H001054 = db.StringProperty(required = False)
    H001055 = db.StringProperty(required = False)
    H001056 = db.StringProperty(required = False)
    H001057 = db.StringProperty(required = False)
    H001058 = db.StringProperty(required = False)
    H001059 = db.StringProperty(required = False)
    H001060 = db.StringProperty(required = False)
    H001061 = db.StringProperty(required = False)
    H001062 = db.StringProperty(required = False)
    H001063 = db.StringProperty(required = False)
    H001064 = db.StringProperty(required = False)
    H001065 = db.StringProperty(required = False)
    H001066 = db.StringProperty(required = False)
    H001067 = db.StringProperty(required = False)
    H001068 = db.StringProperty(required = False)
    H001069 = db.StringProperty(required = False)
    H001070 = db.StringProperty(required = False)
    H001071 = db.StringProperty(required = False)
    H001072 = db.StringProperty(required = False)
    H001073 = db.StringProperty(required = False)
    I000024 = db.StringProperty(required = False)
    I000055 = db.StringProperty(required = False)
    I000056 = db.StringProperty(required = False)
    I000057 = db.StringProperty(required = False)
    J000032 = db.StringProperty(required = False)
    J000126 = db.StringProperty(required = False)
    J000174 = db.StringProperty(required = False)
    J000177 = db.StringProperty(required = False)
    J000255 = db.StringProperty(required = False)
    J000283 = db.StringProperty(required = False)
    J000285 = db.StringProperty(required = False)
    J000288 = db.StringProperty(required = False)
    J000289 = db.StringProperty(required = False)
    J000290 = db.StringProperty(required = False)
    J000291 = db.StringProperty(required = False)
    J000292 = db.StringProperty(required = False)
    J000293 = db.StringProperty(required = False)
    J000294 = db.StringProperty(required = False)
    J000295 = db.StringProperty(required = False)
    J000296 = db.StringProperty(required = False)
    J000297 = db.StringProperty(required = False)
    K000009 = db.StringProperty(required = False)
    K000148 = db.StringProperty(required = False)
    K000172 = db.StringProperty(required = False)
    K000188 = db.StringProperty(required = False)
    K000210 = db.StringProperty(required = False)
    K000220 = db.StringProperty(required = False)
    K000305 = db.StringProperty(required = False)
    K000336 = db.StringProperty(required = False)
    K000352 = db.StringProperty(required = False)
    K000360 = db.StringProperty(required = False)
    K000362 = db.StringProperty(required = False)
    K000363 = db.StringProperty(required = False)
    K000367 = db.StringProperty(required = False)
    K000368 = db.StringProperty(required = False)
    K000369 = db.StringProperty(required = False)
    K000375 = db.StringProperty(required = False)
    K000376 = db.StringProperty(required = False)
    K000378 = db.StringProperty(required = False)
    K000379 = db.StringProperty(required = False)
    K000380 = db.StringProperty(required = False)
    K000381 = db.StringProperty(required = False)
    K000382 = db.StringProperty(required = False)
    K000383 = db.StringProperty(required = False)
    K000384 = db.StringProperty(required = False)
    K000385 = db.StringProperty(required = False)
    K000386 = db.StringProperty(required = False)
    K000387 = db.StringProperty(required = False)
    K000388 = db.StringProperty(required = False)
    L000111 = db.StringProperty(required = False)
    L000123 = db.StringProperty(required = False)
    L000174 = db.StringProperty(required = False)
    L000261 = db.StringProperty(required = False)
    L000263 = db.StringProperty(required = False)
    L000274 = db.StringProperty(required = False)
    L000287 = db.StringProperty(required = False)
    L000304 = db.StringProperty(required = False)
    L000397 = db.StringProperty(required = False)
    L000480 = db.StringProperty(required = False)
    L000491 = db.StringProperty(required = False)
    L000504 = db.StringProperty(required = False)
    L000517 = db.StringProperty(required = False)
    L000550 = db.StringProperty(required = False)
    L000551 = db.StringProperty(required = False)
    L000553 = db.StringProperty(required = False)
    L000554 = db.StringProperty(required = False)
    L000557 = db.StringProperty(required = False)
    L000559 = db.StringProperty(required = False)
    L000560 = db.StringProperty(required = False)
    L000562 = db.StringProperty(required = False)
    L000563 = db.StringProperty(required = False)
    L000564 = db.StringProperty(required = False)
    L000565 = db.StringProperty(required = False)
    L000566 = db.StringProperty(required = False)
    L000567 = db.StringProperty(required = False)
    L000569 = db.StringProperty(required = False)
    L000570 = db.StringProperty(required = False)
    L000571 = db.StringProperty(required = False)
    L000573 = db.StringProperty(required = False)
    L000574 = db.StringProperty(required = False)
    L000575 = db.StringProperty(required = False)
    L000576 = db.StringProperty(required = False)
    L000577 = db.StringProperty(required = False)
    L000578 = db.StringProperty(required = False)
    L000579 = db.StringProperty(required = False)
    L000580 = db.StringProperty(required = False)
    L000581 = db.StringProperty(required = False)
    L000582 = db.StringProperty(required = False)
    L000583 = db.StringProperty(required = False)
    L000584 = db.StringProperty(required = False)
    L000585 = db.StringProperty(required = False)
    M000087 = db.StringProperty(required = False)
    M000133 = db.StringProperty(required = False)
    M000303 = db.StringProperty(required = False)
    M000309 = db.StringProperty(required = False)
    M000312 = db.StringProperty(required = False)
    M000355 = db.StringProperty(required = False)
    M000404 = db.StringProperty(required = False)
    M000485 = db.StringProperty(required = False)
    M000508 = db.StringProperty(required = False)
    M000639 = db.StringProperty(required = False)
    M000689 = db.StringProperty(required = False)
    M000702 = db.StringProperty(required = False)
    M000725 = db.StringProperty(required = False)
    M000933 = db.StringProperty(required = False)
    M000934 = db.StringProperty(required = False)
    M001111 = db.StringProperty(required = False)
    M001134 = db.StringProperty(required = False)
    M001137 = db.StringProperty(required = False)
    M001138 = db.StringProperty(required = False)
    M001139 = db.StringProperty(required = False)
    M001142 = db.StringProperty(required = False)
    M001143 = db.StringProperty(required = False)
    M001144 = db.StringProperty(required = False)
    M001149 = db.StringProperty(required = False)
    M001150 = db.StringProperty(required = False)
    M001151 = db.StringProperty(required = False)
    M001153 = db.StringProperty(required = False)
    M001154 = db.StringProperty(required = False)
    M001155 = db.StringProperty(required = False)
    M001156 = db.StringProperty(required = False)
    M001157 = db.StringProperty(required = False)
    M001158 = db.StringProperty(required = False)
    M001159 = db.StringProperty(required = False)
    M001160 = db.StringProperty(required = False)
    M001163 = db.StringProperty(required = False)
    M001165 = db.StringProperty(required = False)
    M001166 = db.StringProperty(required = False)
    M001169 = db.StringProperty(required = False)
    M001170 = db.StringProperty(required = False)
    M001171 = db.StringProperty(required = False)
    M001176 = db.StringProperty(required = False)
    M001177 = db.StringProperty(required = False)
    M001179 = db.StringProperty(required = False)
    M001180 = db.StringProperty(required = False)
    M001181 = db.StringProperty(required = False)
    M001182 = db.StringProperty(required = False)
    M001183 = db.StringProperty(required = False)
    M001184 = db.StringProperty(required = False)
    M001185 = db.StringProperty(required = False)
    M001187 = db.StringProperty(required = False)
    M001188 = db.StringProperty(required = False)
    M001189 = db.StringProperty(required = False)
    M001190 = db.StringProperty(required = False)
    M001191 = db.StringProperty(required = False)
    M001192 = db.StringProperty(required = False)
    M001193 = db.StringProperty(required = False)
    M001194 = db.StringProperty(required = False)
    M001195 = db.StringProperty(required = False)
    M001196 = db.StringProperty(required = False)
    M001197 = db.StringProperty(required = False)
    N000002 = db.StringProperty(required = False)
    N000015 = db.StringProperty(required = False)
    N000032 = db.StringProperty(required = False)
    N000127 = db.StringProperty(required = False)
    N000147 = db.StringProperty(required = False)
    N000179 = db.StringProperty(required = False)
    N000180 = db.StringProperty(required = False)
    N000181 = db.StringProperty(required = False)
    N000182 = db.StringProperty(required = False)
    N000184 = db.StringProperty(required = False)
    N000185 = db.StringProperty(required = False)
    N000186 = db.StringProperty(required = False)
    N000187 = db.StringProperty(required = False)
    N000188 = db.StringProperty(required = False)
    N000189 = db.StringProperty(required = False)
    O000085 = db.StringProperty(required = False)
    O000168 = db.StringProperty(required = False)
    O000169 = db.StringProperty(required = False)
    O000170 = db.StringProperty(required = False)
    P000034 = db.StringProperty(required = False)
    P000096 = db.StringProperty(required = False)
    P000099 = db.StringProperty(required = False)
    P000197 = db.StringProperty(required = False)
    P000258 = db.StringProperty(required = False)
    P000265 = db.StringProperty(required = False)
    P000373 = db.StringProperty(required = False)
    P000449 = db.StringProperty(required = False)
    P000523 = db.StringProperty(required = False)
    P000583 = db.StringProperty(required = False)
    P000585 = db.StringProperty(required = False)
    P000587 = db.StringProperty(required = False)
    P000588 = db.StringProperty(required = False)
    P000590 = db.StringProperty(required = False)
    P000591 = db.StringProperty(required = False)
    P000592 = db.StringProperty(required = False)
    P000593 = db.StringProperty(required = False)
    P000594 = db.StringProperty(required = False)
    P000595 = db.StringProperty(required = False)
    P000596 = db.StringProperty(required = False)
    P000597 = db.StringProperty(required = False)
    P000598 = db.StringProperty(required = False)
    P000599 = db.StringProperty(required = False)
    P000601 = db.StringProperty(required = False)
    P000602 = db.StringProperty(required = False)
    P000603 = db.StringProperty(required = False)
    P000604 = db.StringProperty(required = False)
    P000605 = db.StringProperty(required = False)
    P000606 = db.StringProperty(required = False)
    P000607 = db.StringProperty(required = False)
    P000608 = db.StringProperty(required = False)
    P000609 = db.StringProperty(required = False)
    P000610 = db.StringProperty(required = False)
    P000611 = db.StringProperty(required = False)
    P000612 = db.StringProperty(required = False)
    Q000023 = db.StringProperty(required = False)
    Q000024 = db.StringProperty(required = False)
    R000011 = db.StringProperty(required = False)
    R000053 = db.StringProperty(required = False)
    R000122 = db.StringProperty(required = False)
    R000146 = db.StringProperty(required = False)
    R000170 = db.StringProperty(required = False)
    R000307 = db.StringProperty(required = False)
    R000361 = db.StringProperty(required = False)
    R000395 = db.StringProperty(required = False)
    R000409 = db.StringProperty(required = False)
    R000435 = db.StringProperty(required = False)
    R000462 = db.StringProperty(required = False)
    R000486 = db.StringProperty(required = False)
    R000487 = db.StringProperty(required = False)
    R000515 = db.StringProperty(required = False)
    R000570 = db.StringProperty(required = False)
    R000571 = db.StringProperty(required = False)
    R000572 = db.StringProperty(required = False)
    R000573 = db.StringProperty(required = False)
    R000575 = db.StringProperty(required = False)
    R000576 = db.StringProperty(required = False)
    R000577 = db.StringProperty(required = False)
    R000578 = db.StringProperty(required = False)
    R000580 = db.StringProperty(required = False)
    R000581 = db.StringProperty(required = False)
    R000582 = db.StringProperty(required = False)
    R000583 = db.StringProperty(required = False)
    R000584 = db.StringProperty(required = False)
    R000585 = db.StringProperty(required = False)
    R000586 = db.StringProperty(required = False)
    R000587 = db.StringProperty(required = False)
    R000588 = db.StringProperty(required = False)
    R000589 = db.StringProperty(required = False)
    R000590 = db.StringProperty(required = False)
    R000591 = db.StringProperty(required = False)
    R000592 = db.StringProperty(required = False)
    R000593 = db.StringProperty(required = False)
    R000594 = db.StringProperty(required = False)
    R000595 = db.StringProperty(required = False)
    R000597 = db.StringProperty(required = False)
    R000598 = db.StringProperty(required = False)
    R000599 = db.StringProperty(required = False)
    R000600 = db.StringProperty(required = False)
    R000601 = db.StringProperty(required = False)
    R000602 = db.StringProperty(required = False)
    R000603 = db.StringProperty(required = False)
    R000604 = db.StringProperty(required = False)
    R000605 = db.StringProperty(required = False)
    S000018 = db.StringProperty(required = False)
    S000030 = db.StringProperty(required = False)
    S000033 = db.StringProperty(required = False)
    S000051 = db.StringProperty(required = False)
    S000148 = db.StringProperty(required = False)
    S000185 = db.StringProperty(required = False)
    S000244 = db.StringProperty(required = False)
    S000248 = db.StringProperty(required = False)
    S000250 = db.StringProperty(required = False)
    S000320 = db.StringProperty(required = False)
    S000344 = db.StringProperty(required = False)
    S000364 = db.StringProperty(required = False)
    S000480 = db.StringProperty(required = False)
    S000510 = db.StringProperty(required = False)
    S000522 = db.StringProperty(required = False)
    S000583 = db.StringProperty(required = False)
    S000663 = db.StringProperty(required = False)
    S000770 = db.StringProperty(required = False)
    S000810 = db.StringProperty(required = False)
    S000822 = db.StringProperty(required = False)
    S000937 = db.StringProperty(required = False)
    S001141 = db.StringProperty(required = False)
    S001145 = db.StringProperty(required = False)
    S001148 = db.StringProperty(required = False)
    S001150 = db.StringProperty(required = False)
    S001154 = db.StringProperty(required = False)
    S001155 = db.StringProperty(required = False)
    S001156 = db.StringProperty(required = False)
    S001157 = db.StringProperty(required = False)
    S001162 = db.StringProperty(required = False)
    S001164 = db.StringProperty(required = False)
    S001165 = db.StringProperty(required = False)
    S001168 = db.StringProperty(required = False)
    S001170 = db.StringProperty(required = False)
    S001171 = db.StringProperty(required = False)
    S001172 = db.StringProperty(required = False)
    S001174 = db.StringProperty(required = False)
    S001175 = db.StringProperty(required = False)
    S001176 = db.StringProperty(required = False)
    S001177 = db.StringProperty(required = False)
    S001179 = db.StringProperty(required = False)
    S001180 = db.StringProperty(required = False)
    S001181 = db.StringProperty(required = False)
    S001182 = db.StringProperty(required = False)
    S001183 = db.StringProperty(required = False)
    S001184 = db.StringProperty(required = False)
    S001185 = db.StringProperty(required = False)
    S001186 = db.StringProperty(required = False)
    S001187 = db.StringProperty(required = False)
    S001188 = db.StringProperty(required = False)
    S001189 = db.StringProperty(required = False)
    S001190 = db.StringProperty(required = False)
    S001191 = db.StringProperty(required = False)
    S001192 = db.StringProperty(required = False)
    S001193 = db.StringProperty(required = False)
    S001194 = db.StringProperty(required = False)
    S001195 = db.StringProperty(required = False)
    S001196 = db.StringProperty(required = False)
    S001197 = db.StringProperty(required = False)
    S001198 = db.StringProperty(required = False)
    T000193 = db.StringProperty(required = False)
    T000238 = db.StringProperty(required = False)
    T000250 = db.StringProperty(required = False)
    T000266 = db.StringProperty(required = False)
    T000326 = db.StringProperty(required = False)
    T000459 = db.StringProperty(required = False)
    T000460 = db.StringProperty(required = False)
    T000461 = db.StringProperty(required = False)
    T000462 = db.StringProperty(required = False)
    T000463 = db.StringProperty(required = False)
    T000464 = db.StringProperty(required = False)
    T000465 = db.StringProperty(required = False)
    T000467 = db.StringProperty(required = False)
    T000468 = db.StringProperty(required = False)
    T000469 = db.StringProperty(required = False)
    T000470 = db.StringProperty(required = False)
    T000471 = db.StringProperty(required = False)
    T000472 = db.StringProperty(required = False)
    T000473 = db.StringProperty(required = False)
    T000474 = db.StringProperty(required = False)
    T000475 = db.StringProperty(required = False)
    T000476 = db.StringProperty(required = False)
    U000031 = db.StringProperty(required = False)
    U000038 = db.StringProperty(required = False)
    U000039 = db.StringProperty(required = False)
    V000081 = db.StringProperty(required = False)
    V000108 = db.StringProperty(required = False)
    V000127 = db.StringProperty(required = False)
    V000128 = db.StringProperty(required = False)
    V000129 = db.StringProperty(required = False)
    V000130 = db.StringProperty(required = False)
    V000131 = db.StringProperty(required = False)
    V000132 = db.StringProperty(required = False)
    W000187 = db.StringProperty(required = False)
    W000207 = db.StringProperty(required = False)
    W000215 = db.StringProperty(required = False)
    W000413 = db.StringProperty(required = False)
    W000437 = db.StringProperty(required = False)
    W000672 = db.StringProperty(required = False)
    W000738 = db.StringProperty(required = False)
    W000779 = db.StringProperty(required = False)
    W000791 = db.StringProperty(required = False)
    W000795 = db.StringProperty(required = False)
    W000796 = db.StringProperty(required = False)
    W000797 = db.StringProperty(required = False)
    W000798 = db.StringProperty(required = False)
    W000799 = db.StringProperty(required = False)
    W000800 = db.StringProperty(required = False)
    W000802 = db.StringProperty(required = False)
    W000803 = db.StringProperty(required = False)
    W000804 = db.StringProperty(required = False)
    W000805 = db.StringProperty(required = False)
    W000806 = db.StringProperty(required = False)
    W000807 = db.StringProperty(required = False)
    W000808 = db.StringProperty(required = False)
    W000809 = db.StringProperty(required = False)
    W000810 = db.StringProperty(required = False)
    W000811 = db.StringProperty(required = False)
    W000812 = db.StringProperty(required = False)
    W000813 = db.StringProperty(required = False)
    W000814 = db.StringProperty(required = False)
    W000815 = db.StringProperty(required = False)
    W000816 = db.StringProperty(required = False)
    W000817 = db.StringProperty(required = False)
    W000818 = db.StringProperty(required = False)
    W000819 = db.StringProperty(required = False)
    W000820 = db.StringProperty(required = False)
    W000821 = db.StringProperty(required = False)
    W000822 = db.StringProperty(required = False)
    Y000031 = db.StringProperty(required = False)
    Y000033 = db.StringProperty(required = False)
    Y000062 = db.StringProperty(required = False)
    Y000063 = db.StringProperty(required = False)
    Y000064 = db.StringProperty(required = False)
    Y000065 = db.StringProperty(required = False)
    Y000066 = db.StringProperty(required = False)
    Z000017 = db.StringProperty(required = False)
    Z000018 = db.StringProperty(required = False)


class State(db.Model):
    name = db.StringProperty(required = True)
    abbreviation = db.StringProperty(required = True)
    num_districts = db.IntegerProperty(required = True)
    senior_senator = db.StringProperty(required = True)
    junior_senator = db.StringProperty(required = True)

class District(db.Model):
	state = db.StringProperty(required = True)
	num = db.IntegerProperty(required = True)
	representative = db.StringProperty(required = True)

class Senator(db.Model):
    bioguide_id = db.StringProperty(required = True)
    state = db.StringProperty(required = True)
    rank = db.StringProperty(required = True)
    name = db.StringProperty(required = True)
    gender = db.StringProperty(required = True)
    party = db.StringProperty(required = True)
    fyio = db.IntegerProperty(required = True)
    fbid = db.StringProperty(required = True)
    twid = db.StringProperty(required = True)
    ployalty = db.IntegerProperty(required = True)
    enacted = db.IntegerProperty(required = True)
    sponsored = db.IntegerProperty(required = True)
    cosponsored = db.IntegerProperty(required = True)
    li = db.IntegerProperty(required = True)

class Representative(db.Model):
    bioguide_id = db.StringProperty(required = True)
    state = db.StringProperty(required = True)
    district = db.IntegerProperty(required = True)
    name = db.StringProperty(required = True)
    gender = db.StringProperty(required = True)
    party = db.StringProperty(required = True)
    fyio = db.IntegerProperty(required = True)
    fbid = db.StringProperty(required = True)
    twid = db.StringProperty(required = True)
    ployalty = db.IntegerProperty(required = True)
    enacted = db.IntegerProperty(required = True)
    sponsored = db.IntegerProperty(required = True)
    cosponsored = db.IntegerProperty(required = True)
    li = db.IntegerProperty(required = True)

class NewsLetterUser(db.Model):
    created = db.DateTimeProperty(required = True, auto_now = True)
    email = db.StringProperty(required = True)

    @classmethod
    def by_email(cls, email):
        u = cls.all().filter('email =', email).get()
        return u

class DatastoreFile(db.Model):
  data = db.BlobProperty(required=True)
  mimetype = db.StringProperty(required=True)

class NationalDemocraticPrimary(db.Model):
    pollster = db.StringProperty(required=True)
    start_date = db.DateTimeProperty(required=True)
    end_date = db.DateTimeProperty(required=True)
    entry_date = db.DateTimeProperty(required=True)
    popsize = db.IntegerProperty(required=True)
    poptype = db.StringProperty(required=True)
    mode = db.StringProperty(required=True)
    hill = db.IntegerProperty(required=False)
    sanders = db.IntegerProperty(required=False)
    omalley = db.IntegerProperty(required=False)
    chafee = db.IntegerProperty(required=False)
    webb = db.IntegerProperty(required=False)
    biden = db.IntegerProperty(required=False)
    undecided = db.IntegerProperty(required=False)
    url = db.StringProperty(required=True)

class NationalRepublicanPrimary(db.Model):
    pollster = db.StringProperty(required=True)
    start_date = db.DateTimeProperty(required=True)
    end_date = db.DateTimeProperty(required=True)
    entry_date = db.DateTimeProperty(required=True)
    popsize = db.IntegerProperty(required=True)
    poptype = db.StringProperty(required=True)
    mode = db.StringProperty(required=True)
    trump = db.IntegerProperty(required=False)
    cruz = db.IntegerProperty(required=False)
    rubio = db.IntegerProperty(required=False)
    carson = db.IntegerProperty(required=False)
    bush = db.IntegerProperty(required=False)
    christie = db.IntegerProperty(required=False)
    paul = db.IntegerProperty(required=False)
    fiorina = db.IntegerProperty(required=False)
    huckabee = db.IntegerProperty(required=False)
    kasich = db.IntegerProperty(required=False)
    santorum = db.IntegerProperty(required=False)
    gilmore = db.IntegerProperty(required=False)
    gram = db.IntegerProperty(required=False)
    jindal = db.IntegerProperty(required=False)
    pataki = db.IntegerProperty(required=False)
    perry = db.IntegerProperty(required=False)
    walker = db.IntegerProperty(required=False)
    undecided = db.IntegerProperty(required=False)
    url = db.StringProperty(required=True)

class Politician(db.Model):
    in_office = db.StringProperty(required = True)
    party = db.StringProperty(required = True)
    gender = db.StringProperty(required = True)
    state = db.StringProperty(required = True)
    state_name = db.StringProperty(required = True)
    distrank = db.StringProperty(required = True)
    chamber = db.StringProperty(required = True)
    birthday = db.StringProperty(required = True)
    fyio = db.IntegerProperty(required = True)
    bioguide_id = db.StringProperty(required = True)
    crp_id = db.StringProperty(required = True)
    fec_ids = db.StringProperty(required = True)
    name = db.StringProperty(required = True)
    phone = db.StringProperty(required = True)
    website = db.StringProperty(required = True)
    contact_form = db.StringProperty(required = True)
    twitter_id = db.StringProperty(required = True)
    youtube_id = db.StringProperty(required = True)
    facebook_id = db.StringProperty(required = True)


#--------------------------Pages----------------------------------------
class BaseHandler(webapp2.RequestHandler):
    year = 2015
    signup_link = '<a href="/signup" class="user_links" id="signup_link">Signup</a>'
    login_link = '<a href="/login" class="user_links" id="login_link">Login</a>'
    logout_link = '<a href="/logout" class="user_links" id="logout_link">Logout:</a>'
    api_url = 'https://congress.api.sunlightfoundation.com/legislators?%(method)s&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
    locator_url = 'https://congress.api.sunlightfoundation.com/districts/locate?%(method)s&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
    def client_token():
        return braintree.ClientToken.generate()

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; expires= Wed, 01 Jan 2020 11:59:59 EST; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.delete_cookie('user_id')

    def address_to_district(self, address):
        #geocoding
        formated_address = address.replace(' ', '+')
        geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&components=zip:USA&key=AIzaSyAUhiPtO7SqZJC59eQ6JyYJGm8cLvmnbbs' % formated_address
        geo = urllib2.urlopen(geocode_url)
        cg = geo.read()
        j_geocode = json.loads(cg)
        status = j_geocode['status']
        if status != 'OK':
            msg = 'invalid address'
            return msg
        #converting to district
        latitude = j_geocode['results'][0]['geometry']['location']['lat']
        longitude = j_geocode['results'][0]['geometry']['location']['lng']
        return self.latlngToDistrict(latitude, longitude)

    def latlngToDistrict(self, lat, lng):
        ll = 'latitude=%(lat)s&longitude=%(lng)s' % {'lat': lat, 'lng': lng}
        p_find_district = urllib2.urlopen(self.locator_url%{'method':ll})
        cd = p_find_district.read()
        j_district = json.loads(cd)
        #extract values from json file
        user_district = '%s:%s' % (j_district["results"][0]["state"], j_district["results"][0]["district"])
        self.set_secure_cookie('district', str(user_district))
        return user_district

    def zip_to_district(self, zip):
        method = 'zip=%s' % zip
        p_find_district = urllib2.urlopen(self.locator_url%{'method':method})
        cd = p_find_district.read()
        return cd

    def append_district(self, district):
        if not self.user:
            return 'error adding district'

        u = self.user
        u.district = district
        u.put()

    def get_politician_ids(self,dist):
        state, district = dist.split(':')
        s = GqlQuery('SELECT senior_senator, junior_senator FROM State WHERE abbreviation=:1', state).get()
        q = District.all()
        q.filter('state', state)
        h = q.filter('num', 3).get()
        politicians = dict(ss=s.senior_senator, js=s.junior_senator, hr=h.representative)
        return politicians

    def getHr(self, dist):
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        rep = GqlQuery('SELECT * FROM Representative WHERE state=\'%s\' and district=%s' %(state, district)).get()
        hr = dict(hrbioguideid = rep.bioguide_id,
                hrpic = state+'_'+district,
                hrstate = rep.state,
                hrdistrict = rep.district,
                hrname = rep.name.replace('_', ' '),
                hrgender = rep.gender,
                hrparty = rep.party,
                hrfyio = rep.fyio,
                hrfbid = rep.fbid,
                hrtwid = rep.twid,
                hrployalty = rep.ployalty,
                hrenacted = rep.enacted,
                hrsponsored = rep.sponsored,
                hrcosponsored = rep.cosponsored,
                hrli = rep.li)
        return hr

    def getSs(self, dist):
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        rep = GqlQuery('SELECT * FROM Senator WHERE state=\'%s\' and rank=\'S\'' %(state)).get()
        ss = dict(ssbioguideid = rep.bioguide_id,
                sspic = state+'_SS',
                ssstate = rep.state,
                ssrank = 'S',
                ssname = rep.name.replace('_', ' '),
                ssgender = rep.gender,
                ssparty = rep.party,
                ssfyio = rep.fyio,
                ssfbid = rep.fbid,
                sstwid = rep.twid,
                ssployalty = rep.ployalty,
                ssenacted = rep.enacted,
                sssponsored = rep.sponsored,
                sscosponsored = rep.cosponsored,
                ssli = rep.li)
        return ss

    def getJs(self, dist):
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        rep = GqlQuery('SELECT * FROM Senator WHERE state=\'%s\' and rank=\'J\'' %(state)).get()
        js = dict(jsbioguideid = rep.bioguide_id,
                jspic = state+'_JS',
                jsstate = rep.state,
                jsrank = 'J',
                jsname = rep.name.replace('_', ' '),
                jsgender = rep.gender,
                jsparty = rep.party,
                jsfyio = rep.fyio,
                jsfbid = rep.fbid,
                jstwid = rep.twid,
                jsployalty = rep.ployalty,
                jsenacted = rep.enacted,
                jssponsored = rep.sponsored,
                jscosponsored = rep.cosponsored,
                jsli = rep.li)
        return js

    def getBig2(self):
        #returns a json file with the basic info for the two most powerful people in congress
        smj = self.getSs('KY:3')
        sfth = self.getHr('WI:1')
        big2 = smj.copy()
        big2.update(sfth)
        big2['smjlpic'] = 'KY_SS'
        big2['spthpic'] = 'WI_1'
        big2json = json.dumps(big2)
        return big2json

    def pullReps(self, district):
        hr = self.getHr(district)
        ss = self.getSs(district)
        js = self.getJs(district)
        reps = hr.copy()
        reps.update(ss)
        reps.update(js)
        reps['district'] = district
        repsjson = json.dumps(reps)
        return repsjson

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

class UploadHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
 
        html_string = """
         <form action="%s" method="POST" enctype="multipart/form-data">
        Upload File:
        <input type="file" name="file"> <br>
        <input type="submit" name="submit" value="Submit">
        </form>""" % upload_url
 
        self.response.out.write(html_string)

class Upload(blobstore_handlers.BlobstoreUploadHandler):

    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        info = upload_files[0]
 
        #process_state_csv(info)
        #process_district_csv(info)
        #process_senator_csv(info)
        #process_rep_csv(info)
        #process_stat_csv(info)
        #process_nationalpolls(info, 'R')
        #process_politician_csv(info)
        #process_votes_csv(info)
        process_ind_votes_csv(info)
        self.redirect("/")

class Landing(BaseHandler):
    def get(self):
        self.render("vprop.html")
    def post(self):
        self.render('vprop.html')

class About(BaseHandler):
    def get(self):
        self.render('about.html')
    def post(self):
        self.render('about.html')

class Sources(BaseHandler):
    def get(self):
        self.render('sources.html')
    def post(self):
        self.render('sources.html')

class NewsLetter(BaseHandler):
    def get(self):
        self.render('esf.html')

    def post(self):
        email = self.request.get('email')
        error_message = 'none'
        have_error = False
        logging.error(email)
        if not valid_email(email):
            error_message = "invalid email"
            have_error = True

        if have_error:
            self.write(error_message)
        else:
            e = NewsLetterUser.by_email(email)
            if e:
                error_message='already on list'
                self.write(error_message)
            else: #vetted email: add to db, send thankyou email, and success code to front end
                potential_signee=NewsLetterUser(email=email)
                potential_signee.put()
                self.write('success')
                #send thank you email
                sender_address = "glasscapitol.com Mailing List <glasscapitol@gmail.com>"
                subject = "Welcome to the NewsLetter!!"
                body = 'congrats on becoming a boss'
                mail.send_mail(sender_address, email, subject, body)

class Feedback(BaseHandler):
    def get(self):
        self.render('feedback.html')
    def post(self):
        self.render('feedback.html')

class Vprop(BaseHandler):
    def get(self):
        self.render('interactives.html')

    def post(self):
        self.render('interactives.html')

class PollServer(BaseHandler):
    def get(self):
        self.redirect('/')

    def post(self):
        dataname = self.request.get('dataname')
        #pull that data associated with dataname, package it, and return it
        data = ''
        if dataname == 'repub_national':
            data = 'entry_date,trump,cruz,rubio,carson,bush,christie,paul,fiorina,huckabee,kasich,santorum,gilmore,gram,jindal,pataki,perry,walker,undecided\n'
            for e in GqlQuery("SELECT entry_date,trump,cruz,rubio,carson,bush,christie,paul,fiorina,huckabee,kasich,santorum,gilmore,gram,jindal,pataki,perry,walker,undecided FROM NationalRepublicanPrimary WHERE entry_date > DATETIME(2014,12,31) ORDER BY entry_date DESC"):
                line = str(e.entry_date)+','+str(e.trump)+','+str(e.cruz)+','+str(e.rubio)+','+str(e.carson)+','+str(e.bush)+','+str(e.christie)+','+str(e.paul)+','+str(e.fiorina)+','+str(e.huckabee)+','+str(e.kasich)+','+str(e.santorum)+','+str(e.gilmore)+','+str(e.gram)+','+str(e.jindal)+','+str(e.pataki)+','+str(e.perry)+','+str(e.walker)+','+str(e.undecided)+'\n'
                data += line
        elif dataname == 'dem_national':
            data = 'entry_date,hill,sanders,omalley,chafee,webb,biden,undecided\n'
            for e in GqlQuery("SELECT entry_date,hill,sanders,omalley,chafee,webb,biden,undecided FROM NationalDemocraticPrimary WHERE entry_date > DATETIME(2014,12,31) ORDER BY entry_date DESC"):
                line = str(e.entry_date)+','+str(e.hill)+','+str(e.sanders)+','+str(e.omalley)+','+str(e.chafee)+','+str(e.webb)+','+str(e.biden)+','+str(e.undecided)+'\n'
                data += line
        
        self.response.out.write(data)

class Update(BaseHandler):
    def getNationalPolls(self):
        #make api call to get most recent batch of poll data
        #logging.error('whats up')
        #compare api data to most recent data from datastore IF !=, append db with data
        #(datastore classes are (NationalDemocraticPrimary, NationalRepuclicanPrimary)

        #return two csv strings of polling data formatted for graph only

        dem_url = 'http://elections.huffingtonpost.com/pollster/api/polls.json?topic=2016-president-dem-primary'
        gop_url = 'http://elections.huffingtonpost.com/pollster/api/polls.json?topic=2016-president-gop-primary'

        dem = urllib2.urlopen(dem_url)
        gop = urllib2.urlopen(gop_url)
        demo = dem.read()
        repu = gop.read()
        demdata = json.loads(demo)
        gopdata = json.loads(repu)
        tru, sant, rub, pau, pat, kas, bus, huc, fio, cru, chri, car, gil, gra, jin, per, wal, rundec = -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1
        todaydate = datetime.today()
        topdategop = datetime.min
        topdatedem = datetime.min
        tempgopdate = GqlQuery("SELECT * FROM NationalRepublicanPrimary ORDER BY end_date DESC").get()
        tempdemdate = GqlQuery("SELECT * FROM NationalDemocraticPrimary ORDER BY end_date DESC").get()
        topdategop = tempgopdate.end_date
        topdatedem = tempdemdate.end_date
        for i in gopdata:
            polls = i["pollster"]
            notend = i["end_date"]
            notstart = i["start_date"]
            method = i["method"]
            start = datetime.strptime(notstart, '%Y-%m-%d')
            end = datetime.strptime(notend, '%Y-%m-%d')
            sourceurl = i["source"]
            for j in i["questions"]:
                tru, sant, rub, pau, pat, kas, bus, huc, fio, cru, chri, car, gil, gra, jin, per, wal, rundec = -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1
                if (str(j["topic"]) == "2016-president-gop-primary"):
                    pop = j["subpopulations"][0]["observations"]
                    poptype = j["subpopulations"][0]["name"]
                    for k in j["subpopulations"][0]["responses"]:
                        if (k["choice"] == "Trump"):
                            tru = int(k["value"])
                        if (k["choice"] == "Santorum"):
                            sant = int(k["value"])
                        if (k["choice"] == "Rubio"):
                            rub = int(k["value"])
                        if (k["choice"] == "Rand Paul" or k["choice"] == "Paul"):
                            pau = int(k["value"])
                        if (k["choice"] == "Pataki"):
                            pat = int(k["value"])
                        if (k["choice"] == "Kasich"):
                            kas = int(k["value"])
                        if (k["choice"] == "Jeb Bush" or k["choice"] == "Bush"):
                            bus = int(k["value"])
                        if (k["choice"] == "Huckabee"):
                            huc = int(k["value"])
                        if (k["choice"] == "Fiorina"):
                            fio = int(k["value"])
                        if (k["choice"] == "Cruz"):
                            cru = int(k["value"])
                        if (k["choice"] == "Christie"):
                            chri = int(k["value"])
                        if (k["choice"] == "Carson"):
                            car = int(k["value"])
                    if (end > topdategop):
                        entry = NationalRepublicanPrimary(pollster=polls, start_date=start, end_date=end, entry_date=todaydate, popsize=pop, poptype=poptype, mode=method, trump=tru, cruz=cru, rubio=rub, kasich=kas, carson=car, bush=bus, christie=chri, paul=pau, fiorina=fio, huckabee=huc, santorum=sant, gilmore=gil, gram=gra, jindal=jin, pataki=pat, perry=per, walker=wal, undecided=rundec, url=sourceurl)
                        entry.put()
                            
        cli, sand, omal, cha, web, bid, dundec = -1, -1, -1, -1, -1, -1, -1
        for i in demdata:
            polls = i["pollster"]
            notend = i["end_date"]
            notstart = i["start_date"]
            start = datetime.strptime(notstart, '%Y-%m-%d')
            end = datetime.strptime(notend, '%Y-%m-%d')
            method = i["method"]
            sourceurl = i["source"]
            for j in i["questions"]:
                cli, sand, omal, cha, web, bid, dundec = -1, -1, -1, -1, -1, -1, -1
                if (str(j["topic"]) == "2016-president-dem-primary"):
                    pop = j["subpopulations"][0]["observations"]
                    poptype = j["subpopulations"][0]["name"]
                    for k in j["subpopulations"][0]["responses"]:
                        if (k["choice"] == "Clinton"):
                            cli = int(k["value"])
                        if (k["choice"] == "Sanders"):
                            sand = int(k["value"])
                        if (k["choice"] == "O'Malley"):
                            omal = int(k["value"])
                    if (end > topdatedem):
                        entry = NationalDemocraticPrimary(pollster=polls, start_date=start, end_date=end, entry_date=todaydate, popsize=pop, poptype=poptype, mode=method, hill=cli, sanders=sand, omalley=omal, chafee=cha, webb=web, biden=bid, undecided=dundec, url=sourceurl)
                        entry.put()
    def get(self):
        self.getNationalPolls()
        self.redirect('/')

    def post(self):
        #get type of data to pull
        self.redirect('/')

class Demo(BaseHandler):
    def get(self):
        self.render('demo.html')

    def post(self):
        demo = self.request.get('demo')
        if demo:
            params = self.getBig2()
            self.write(params)

        address = self.request.get('address')
        if address:
            district = self.address_to_district(address)
            logging.error(district)
            repjson = self.pullReps(district)
            self.write(repjson)

        lat = self.request.get('lat')
        lng = self.request.get('lng')
        if lat and lng:
            district = self.latlngToDistrict(lat, lng)
            repjson = self.pullReps(district)
            self.write(repjson)

application = webapp2.WSGIApplication([
    ('/', Landing),
    ('/prop', Vprop),
    ('/feedback', Feedback),
    ('/demo', Demo),
    ('/about', About),
    ('/newsletter', NewsLetter),
    ('/sources', Sources),
    ('/pull/polldata', PollServer),
    ('/updateship', Update),
    ('/up', UploadHandler),
    ('/upload', Upload),
], debug=True)
