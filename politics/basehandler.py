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
import base64
from google.appengine.ext.webapp.util import run_wsgi_app
from datetime import datetime, date, time, timedelta
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.db import GqlQuery
from google.appengine.api import mail
from updatevotes import *
from updatebills import *
from updatepolls import *
from updatecosponsors import *
import databaseclasses
from csvprocessing import *
from basehandler import *
from politics import *


login_session = {}

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = '2A3437B9B29034B7'
sunlight_key = '5a2e18d2e3ed4861a8604e9a5f96a47a'
SESSION_LENGTH = 7200
DB_SESSION_RESET = 600


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

DISTRICT_RE = re.compile(r'^[A-Z]{2}:[0-9]{1,2}')
def valid_district(district):
    return district and DISTRICT_RE.match(district)

#---------------------------User Implementation Functions--------------------------
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def make_salt(length = 30):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(username, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(username + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def weekdaytostr(date):
    daylist = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    return daylist[date]

def monthtostr(date):
    monthlist = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return monthlist[date-1]

def processname(name):
    name = name.split('_')
    for i in range(5):
        name[i] = name[i] + ' '
        if (name[i] == 'None '):
            name[i] = ''
    return name[1] + name[2] + name[0] + name[3]# + name[4]

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
            '%s=%s; expires= Wed, 01 Feb 2017 11:59:59 EST; Path=/' % (name, cookie_val))

    def set_secure_cookiedate(self, name, val, expr):
        weekday = weekdaytostr(expr.weekday())
        exprstr = weekday+', '+str(expr.day)+' '+monthtostr(expr.month)+' '+str(expr.year)+' '+str(expr.hour)+':'+str(expr.minute)+':'+str(expr.second)+' GMT'
        logging.error(exprstr)
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; expires= %s; Path=/' % (name, cookie_val, exprstr))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def is_session_active(self):
        cookie_val = self.request.cookies.get('sid')
        strcookdate = str(cookie_val).split('|')[0].split('--')[1]
        cookid = str(cookie_val).split('|')[0].split('--')[0]
        cookdate = datetime.strptime(strcookdate, '%Y-%m-%d_%H:%M:%S')
        dbsecleft = self.db_session_active(cookid)
        logging.error('db sess secleft: '+str(dbsecleft))
        if cookdate >= datetime.now() and dbsecleft > 0:
            secleft = cookdate - datetime.now()
            secleft = secleft.seconds
            cookdate = datetime.now() + timedelta(seconds=SESSION_LENGTH)
            strcookdate = str(cookdate)
            strcookdate = strcookdate[:10]+'_'+strcookdate[11:19]
            cookie_val = cookie_val[:18]+strcookdate
            self.set_secure_cookiedate('sid', str(cookie_val), cookdate)
            logging.error('Session seconds left: '+str(secleft))
            return secleft
        else:
            return -1

    def db_session_active(self, cookid):
        dbentry = Session.get_by_id(int(cookid))
        if dbentry:
            dbdate = dbentry.expiration
        else:
            dbdate = datetime.min
        if dbdate >= datetime.now():
            if ((dbdate-datetime.now()).seconds <= DB_SESSION_RESET) and ((dbdate-datetime.now()).seconds > 0):
                dbentry.expiration = dbdate+timedelta(seconds=SESSION_LENGTH)
                dbentry.put()
            secleft = dbdate - datetime.now()
            secleft = secleft.seconds
            logging.error('Database seconds left: '+str(secleft))
            return secleft
        else:
            return -1

    def login(self, session, expr):
        exprstr = str(expr)
        exprstr = exprstr[:10]+'_'+exprstr[11:19]
        self.set_secure_cookiedate('sid', str(session.key().id())+'--'+str(exprstr), expr)

    def logout(self):
        self.response.delete_cookie('sid')

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
        logging.error(state)
        logging.error(district)
        rep = GqlQuery('SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'%s\'' %(state, district)).get()
        stats = GqlQuery('SELECT * FROM Politician_Stats WHERE bioguide_id = \'%s\'' % (rep.bioguide_id)).get()
        name = processname(rep.name)
        twitter = rep.twitter_id
        if rep.twitter_id == 'None':
            twitter = ''
        if rep.party == 'R':
            party = 'Republican'
        else:
            party = 'Democrat'
        hr = dict(hrbioguideid = rep.bioguide_id,
                hrpic = state+'_'+district,
                hrstate = rep.state,
                hrstatename = rep.state_name,
                hrdistrict = rep.distrank,
                hrname = name.replace('_', ' '),
                hrgender = rep.gender,
                hrparty = party,
                hrfyio = rep.fyio,
                hrfbid = rep.facebook_id,
                hrtwid = twitter,
                hrwebsite = rep.website,
                hrpartyloyalty = stats.party_loyalty,
                hrlegindex = stats.legislative_index,
                hrsponsored = stats.bills_sponsored,
                hrcosponsored = stats.bills_cosponsored,
                hrattendance = stats.attendance,
                hrnumber_enacted = stats.number_enacted,
                hreffectiveness = stats.effectiveness,
                hrtitle = '%s District %s Representative' % (state, district))
        return hr

    def getSs(self, dist):
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        msg = 'SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'S\'' %(state)
        logging.error(msg)
        rep = GqlQuery('SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'s\'' %(state)).get()
        stats = GqlQuery('SELECT * FROM Politician_Stats WHERE bioguide_id = \'%s\'' % (rep.bioguide_id)).get()
        name = processname(rep.name)
        twitter = rep.twitter_id
        if rep.twitter_id == 'None':
            twitter = ''
        if rep.party == 'R':
            party = 'Republican'
        else:
            party = 'Democrat'
        ss = dict(ssbioguideid = rep.bioguide_id,
                sspic = state+'_SS',
                ssstate = rep.state,
                ssrank = 'S',
                ssname = name.replace('_', ' '),
                ssgender = rep.gender,
                ssparty = party,
                ssfyio = rep.fyio,
                ssfbid = rep.facebook_id,
                sstwid = twitter,
                sswebsite = rep.website,
                sspartyloyalty = stats.party_loyalty,
                sslegindex = stats.legislative_index,
                sssponsored = stats.bills_sponsored,
                sscosponsored = stats.bills_cosponsored,
                ssattendance = stats.attendance,
                ssnumber_enacted = stats.number_enacted,
                sseffectiveness = stats.effectiveness,
                sstitle = '%s Senior Senator' % (state))
        return ss

    def getJs(self, dist):
        logging.error(dist)
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        rep = GqlQuery('SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'j\'' %(state)).get()
        stats = GqlQuery('SELECT * FROM Politician_Stats WHERE bioguide_id = \'%s\'' % (rep.bioguide_id)).get()
        name = processname(rep.name)
        twitter = rep.twitter_id
        if rep.twitter_id == 'None':
            twitter = ''
        if rep.party == 'R':
            party = 'Republican'
        else:
            party = 'Democrat'
        js = dict(jsbioguideid = rep.bioguide_id,
                jspic = state+'_JS',
                jsstate = rep.state,
                jsrank = 'J',
                jsname = name.replace('_', ' '),
                jsgender = rep.gender,
                jsparty = party,
                jsfyio = rep.fyio,
                jsfbid = rep.facebook_id,
                jstwid = twitter,
                jswebsite = rep.website,
                jspartyloyalty = stats.party_loyalty,
                jslegindex = stats.legislative_index,
                jssponsored = stats.bills_sponsored,
                jscosponsored = stats.bills_cosponsored,
                jsattendance = stats.attendance,
                jsnumber_enacted = stats.number_enacted,
                jseffectiveness = stats.effectiveness,
                jstitle = '%s Junior Senator' % (state))
        return js

    def getBig2(self, statlist, basicstats):
        #returns a json file with the basic info for the two most powerful people in congress
        smj = self.getSs('KY:3')
        sfth = self.getHr('WI:1')
        big2 = smj.copy()
        big2.update(sfth)
        big2['hrtitle'] = 'Senate Majority Leader'
        big2['sstitle'] = 'Speaker of the House'
        temprep = ['hr','ss']
        tempstat = basicstats.split(',')
        for i in range(len(temprep)):
            logging.error(i)
            for j in range(len(tempstat)):
                logging.error(j)
                logging.error('%sstat%s'%(temprep[i],str(j+1)))
                if tempstat[j] == '1':
                    big2['%sstat%s'%(temprep[i],str(j+1))] = big2['%spartyloyalty'%(temprep[i])]
                elif tempstat[j] == '2':
                    big2['%sstat%s'%(temprep[i],str(j+1))] = big2['%slegindex'%(temprep[i])]
                elif tempstat[j] == '3':
                    big2['%sstat%s'%(temprep[i],str(j+1))] = big2['%ssponsored'%(temprep[i])]
                elif tempstat[j] == '4':
                    big2['%sstat%s'%(temprep[i],str(j+1))] = big2['%scosponsored'%(temprep[i])]
                elif tempstat[j] == '5':
                    big2['%sstat%s'%(temprep[i],str(j+1))] = big2['%sattendance'%(temprep[i])]
                elif tempstat[j] == '6':
                    big2['%sstat%s'%(temprep[i],str(j+1))] = big2['%snumber_enacted'%(temprep[i])]
                elif tempstat[j] == '7':
                    big2['%sstat%s'%(temprep[i],str(j+1))] = big2['%seffectiveness'%(temprep[i])]
                big2['stat%sname'%(str(j+1))] = statlist[int(tempstat[j])-1]
        return big2

    def pullReps(self, district, statlist, basicstats):
        hr = self.getHr(district)
        ss = self.getSs(district)
        js = self.getJs(district)
        reps = hr.copy()
        reps.update(ss)
        reps.update(js)
        reps['district'] = district
        temprep = ['hr','ss','js']
        tempstat = basicstats.split(',')
        for i in range(len(temprep)):
            for j in range(len(tempstat)):
                if tempstat[j] == '1':
                    reps['%sstat%s'%(temprep[i],str(j+1))] = reps['%spartyloyalty'%(temprep[i])]
                elif tempstat[j] == '2':
                    reps['%sstat%s'%(temprep[i],str(j+1))] = reps['%slegindex'%(temprep[i])]
                elif tempstat[j] == '3':
                    reps['%sstat%s'%(temprep[i],str(j+1))] = reps['%ssponsored'%(temprep[i])]
                elif tempstat[j] == '4':
                    reps['%sstat%s'%(temprep[i],str(j+1))] = reps['%scosponsored'%(temprep[i])]
                elif tempstat[j] == '5':
                    reps['%sstat%s'%(temprep[i],str(j+1))] = reps['%sattendance'%(temprep[i])]
                elif tempstat[j] == '6':
                    reps['%sstat%s'%(temprep[i],str(j+1))] = reps['%snumber_enacted'%(temprep[i])]
                elif tempstat[j] == '7':
                    reps['%sstat%s'%(temprep[i],str(j+1))] = reps['%seffectiveness'%(temprep[i])]
                reps['stat%sname'%(str(j+1))] = statlist[int(tempstat[j])-1]
        return reps
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))