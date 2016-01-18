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
        row_str = row[0]
        temp = row_str.split(',')
        entry = Ind_Votes(bill_id=temp[0], bioguide_id=temp[1], vote=temp[2])
        entry.put()
        if (count%1000 == 0):
            logging.error(count)
        count += 1

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
        process_politician_csv(info)
        #process_votes_csv(info)
        #process_ind_votes_csv(info)
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
