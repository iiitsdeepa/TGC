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

import webapp2
import jinja2
import cgi
from google.appengine.ext.webapp.util import run_wsgi_app

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

#--------------------------Pages----------------------------------------
class BaseHandler(webapp2.RequestHandler):
    year = 2015
    signup_link = '<a href="/signup" class="user_links" id="signup_link">Signup</a>'
    login_link = '<a href="/login" class="user_links" id="login_link">Login</a>'
    logout_link = '<a href="/logout" class="user_links" id="logout_link">Logout:</a>'
    api_url = 'https://congress.api.sunlightfoundation.com/legislators?%(method)s&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
    locator_url = 'https://congress.api.sunlightfoundation.com/districts/locate?%(method)s&apikey=5a2e18d2e3ed4861a8604e9a5f96a47a'
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
        self.latlngToDistrict(latitude, longitude)

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
        process_senator_csv(info)
        #process_rep_csv(info)
        #process_stat_csv(info)
        self.redirect("/")

class Admin(BaseHandler):
    def get(self):
        self.render('admin.html')

    def post(self):
        secret = self.request.get('secret')
        if secret == 'fire':
            self.write('freedom')

class Signup(BaseHandler):
    def post(self):
        username = self.request.get('username')
        email = self.request.get('email')
        password = self.request.get('password')
        have_error = False

        #query the database to ensure the username, and email are unique
        if username and email and password:
            n = User.by_username(username)
            e = User.by_email(email)
            if n and not e: #username is traken
                self.write('1')
            elif e and not n: #email is taken
                self.write('2')
            elif n and e: #username and email are taken
                self.write('3')
            else:
                self.write('success')
                u = User.register(username, email, password)
                u.put()
                self.login(u)

class Login(BaseHandler):
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.write('in')
        else:
            self.write('invalid login')

class Main(BaseHandler):
    def get(self):
        self.render('tmain.html')

    def post(self):
        username = self.request.get('username')
        email = self.request.get('email')
        password = self.request.get('password')

        #query the database to ensure the username, and email are unique
        if username and email and password:
            n = User.by_username(username)
            e = User.by_email(email)
            if n and not e: #username is traken
                self.write('2')
            elif e and not n: #email is taken
                self.write('3')
            elif n and e: #username and email are taken
                self.write('4')
            else:
                self.write('1')
                u = User.register(username, email, password)
                u.put()
                self.login(u)

        zip = self.request.get('zip')
        if zip: #a zip code is given
            zip_json = self.zip_to_district(zip)
            self.write(zip_json)

        address = self.request.get('address')
        if address:
            district = self.address_to_district(address)
            self.write(district)

        lat = self.request.get('lat')
        lng = self.request.get('lng')
        if lat and lng:
            district = self.latlngToDistrict(lat, lng)
            self.write(district)

class Cards(BaseHandler):
    def get_legislators(self, district):
        state, dnum = district.split(':')
        #query the datastore to get the house representative
        msg = "SELECT name, party, fyio FROM Representative WHERE State=\'%s\' AND district=\'%d\'" %(state, int(dnum))
        q = db.GqlQuery(msg)

    def get(self):
        self.render('big3.html')

    def post(self):
        district = self.request.get('district')
        if district: #pull legislator data, and render cards with data
            self.get_legislators(district)
            hrparams = self.getHr(district)
            ssparams = self.getSs(district)
            jsparams = self.getJs(district)
            params = dict(district = district)
            params.update(hrparams)
            params.update(ssparams)
            params.update(jsparams)
            self.render('cards.html', **params)
        else:
            self.render('big3.html')

class Landing(BaseHandler):
    def get(self):
        self.render("landing1.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username = username,
                      email = email)

        if not valid_username(username):
            params['error_username'] = "invalid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "invalid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "non-matching passwords"
            have_error = True

        if not valid_email(email):
            params['error_email'] = "invalid email"
            have_error = True

        if have_error:
            self.render('landing.html', **params)
        else:
            self.redirect('/splash' + username)

class Test(BaseHandler):
    def get(self):
        self.initialize()

class Splash(BaseHandler):
    def get(self):
        if self.user:
            self.render('splash.html')
        else:
            self.redirect('/')

class Mreps(BaseHandler):
    def get(self):
        if self.user:
            self.render('mreps.html')
        else:
            self.redirect('/')

class Pcomp(BaseHandler):
    def get(self):
        if self.user:
            self.render('pcomp.html')
        else:
            self.redirect('/')

class Ccomp(BaseHandler):
    def get(self):
        if self.user:
            self.render('ccomp.html')
        else:
            self.redirect('/')

class Lbranch(BaseHandler):
    def get(self):
        if self.user:
            self.render('lbranch.html')
        else:
            self.redirect('/')

class Jbranch(BaseHandler):
    def get(self):
        if self.user:
            self.render('jbranch.html')
        else:
            self.redirect('/')

class Public(BaseHandler):
    def get(self):
        if self.user:
            self.render('landing.html')
        else:
            self.redirect('/')

class About(BaseHandler):
    def get(self):
        self.render('about.html')

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



application = webapp2.WSGIApplication([
    ('/', Landing),
    ('/admin', Admin),
    ('/signup', Signup),
    ('/login', Login),
    ('/splash', Splash),
    ('/main', Main),
    ('/up', UploadHandler),
    ('/upload', Upload),
    ('/cards', Cards),
    ('/test', Test),
    ('/mreps', Mreps),
    ('/pcomp', Pcomp),
    ('/ccomp', Ccomp),
    ('/lbranch', Lbranch),
    ('/jbranch', Jbranch),
    ('/public', Public),
    ('/about', About),
    ('/newsletter', NewsLetter)
], debug=True)
