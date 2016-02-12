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
from updatevotes import *
from updatebills import *
from updatepolls import *
from updatecosponsors import *
import databaseclasses
from csvprocessing import *

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
        logging.error(state)
        logging.error(district)
        rep = GqlQuery('SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'%s\'' %(state, district)).get()
        name = rep.name.replace('None', '')
        hr = dict(hrbioguideid = rep.bioguide_id,
                hrpic = state+'_'+district,
                hrstate = rep.state,
                hrdistrict = rep.distrank,
                hrname = name.replace('_', ' '),
                hrgender = rep.gender,
                hrparty = rep.party,
                hrfyio = rep.fyio,
                hrfbid = rep.facebook_id,
                hrtwid = rep.twitter_id,)
        return hr

    def getSs(self, dist):
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        msg = 'SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'S\'' %(state)
        logging.error(msg)
        rep = GqlQuery('SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'s\'' %(state)).get()
        name = rep.name.replace('None', '')
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
                )
        return ss

    def getJs(self, dist):
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        rep = GqlQuery('SELECT * FROM Politician WHERE state=\'%s\' and distrank=\'j\'' %(state)).get()
        name = rep.name.replace('None', '')
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
                )
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
        #process_ind_votes_csv(info)
        #process_bill_csv(info)
        #process_cosponsor_csv(info)
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

class UpdateAll(BaseHandler):
    def get(self):
        logging.error('National Polls')
        getNationalPolls()
        logging.error('Votes')
        getVotesUpdate()
        logging.error('Bills')
        getBillsUpdate()
        #logging.error('Cosponsors')
        #getCosponsorsUpdate()
        #self.redirect('/')
        self.response.set_status(200)

    def post(self):
        #get type of data to pull
        self.redirect('/')

class bulkdelete(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        try:
            while True:
                q = db.GqlQuery("SELECT __key__ FROM Bill")
                assert q.count()
                db.delete(q.fetch(200))
                sleep(0.5)
        except Exception, e:
            self.response.out.write(repr(e)+'\n')
            pass

class Marketing(BaseHandler):
    def get(self):
        self.render("personalmarketing.html")
    def post(self):
        self.render("personalmarketing.html")

class Login(BaseHandler):
    def get(self):
        self.render('login.html')

class Signup(BaseHandler):
    def get(self):
        self.render('presignup.html')

    def post(self):
        type = self.request.get('type')
        if type == 'keyform':
            key = self.request.get('key')
            if key == 'is you is':
                self.render('signup.html')
        elif type == 'signupform':
                self.render('about.html')


application = webapp2.WSGIApplication([
    ('/', Landing),
    ('/signup', Signup),
    ('/login', Login),
    ('/prop', Vprop),
    ('/feedback', Feedback),
    ('/about', About),
    ('/newsletter', NewsLetter),
    ('/sources', Sources),
    ('/pull/polldata', PollServer),
    ('/updateall', UpdateAll),
    #('/up', UploadHandler),
    #('/upload', Upload),
    #('/delete', bulkdelete)
    ('/marketing', Marketing)
], debug=True)
