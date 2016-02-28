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
from politics import *
from basehandler import *

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
        logging.error(state)
        logging.error(district)
        rep = GqlQuery('SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'%s\'' %(state, district)).get()
        name = rep.name.replace('_', ' ')
        hr = dict(hrbioguideid = rep.bioguide_id,
                hrpic = state+'_'+district,
                hrstate = rep.state,
                hrstatename = rep.state_name,
                hrdistrict = rep.distrank,
                hrname = name.replace('_', ' '),
                hrgender = rep.gender,
                hrparty = rep.party,
                hrfyio = rep.fyio,
                hrfbid = rep.facebook_id,
                hrtwid = rep.twitter_id,
                hrwebsite = rep.website)
        return hr

    def getSs(self, dist):
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        msg = 'SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'S\'' %(state)
        logging.error(msg)
        rep = GqlQuery('SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'s\'' %(state)).get()
        name = rep.name.replace('_', ' ')
        ss = dict(ssbioguideid = rep.bioguide_id,
                sspic = state+'_SS',
                ssstate = rep.state,
                ssrank = 'S',
                ssname = name.replace('_', ' '),
                ssgender = rep.gender,
                ssparty = rep.party,
                ssfyio = rep.fyio,
                ssfbid = rep.facebook_id,
                sstwid = rep.twitter_id,
                sswebsite = rep.website
                )
        return ss

    def getJs(self, dist):
        logging.error(dist)
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        rep = GqlQuery('SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'j\'' %(state)).get()
        name = rep.name.replace('_', ' ')
        js = dict(jsbioguideid = rep.bioguide_id,
                jspic = state+'_JS',
                jsstate = rep.state,
                jsrank = 'J',
                jsname = name.replace('_', ' '),
                jsgender = rep.gender,
                jsparty = rep.party,
                jsfyio = rep.fyio,
                jsfbid = rep.facebook_id,
                jstwid = rep.twitter_id,
                jswebsite = rep.website
                )
        return js

    def getSfth(self,dist):
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        rep = GqlQuery('SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'%s\'' %(state, district)).get()
        name = rep.name.replace('_', ' ').replace('None','')
        hr = dict(sfthbioguideid = rep.bioguide_id,
                sfthpic = state+'_'+district,
                sfthstate = rep.state,
                sfthdistrict = rep.distrank,
                sfthname = name,
                sfthgender = rep.gender,
                sfthparty = rep.party,
                sfthfyio = rep.fyio,
                sfthfbid = rep.facebook_id,
                sfthtwid = rep.twitter_id,
                sfthwebsite = rep.website
                )
        return hr

    def getSmj(self,dist):
        state, district = dist.split(':')
        rep = GqlQuery('SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'s\'' %(state)).get()
        name = rep.name.replace('_', ' ').replace('NONE', '')
        js = dict(smjbioguideid = rep.bioguide_id,
                smjpic = state+'_SS',
                smjstate = rep.state,
                smjrank = 'S',
                smjname = name,
                smjgender = rep.gender,
                smjparty = rep.party,
                smjfyio = rep.fyio,
                smjfbid = rep.facebook_id,
                smjtwid = rep.twitter_id,
                smjwebsite = rep.website
                )
        return js

    def getBig2(self):
        #returns a json file with the basic info for the two most powerful people in congress
        smj = self.getSmj('KY:3')
        sfth = self.getSfth('WI:1')
        big2 = smj.copy()
        big2.update(sfth)
        big2['smjlpic'] = 'KY_SS'
        big2['spthpic'] = 'WI_1'
        return big2

    def pullReps(self, district):
        big2 = self.getBig2()
        hr = self.getHr(district)
        ss = self.getSs(district)
        js = self.getJs(district)
        reps = hr.copy()
        reps.update(ss)
        reps.update(js)
        reps.update(big2)
        reps['district'] = district
        return reps

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
