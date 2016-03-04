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
import politics
from databaseclasses import *

def getNationalPolls():
    #make api call to get most recent batch of poll data
    #logging.error('whats up')
    #compare api data to most recent data from datastore IF !=, append db with data
    #(datastore classes are (NationalDemocraticPrimary, NationalRepuclicanPrimary)

    #return two csv strings of polling data formatted for graph only

    dem_url = 'http://elections.huffingtonpost.com/pollster/api/polls.json?%stopic=2016-president-dem-primary'
    gop_url = 'http://elections.huffingtonpost.com/pollster/api/polls.json?%stopic=2016-president-gop-primary'
    tempgopdate = GqlQuery("SELECT * FROM NationalRepublicanPrimary ORDER BY entry_date DESC").get()
    try:
        topdategop = tempgopdate.entry_date
    except:
        topdategop = datetime.min
    #logging.error(str(topdategop))
    breakvar = False
    #this for loop goes through each page in the api database, starting at page = 1 (most recent) and going to the end (earliest)
    for x in range(1,100):
        logging.error('GOP page: '+str(x))
        bill_method = 'sort=updated&page=%d&' % (x)
        try:
            gop = urllib2.urlopen(gop_url % bill_method)
        except:
            logging.error('failed or end of things gop')
            gop = []
        repu = gop.read()
        gopdata = json.loads(repu)
        tru, sant, rub, pau, pat, kas, bus, huc, fio, cru, chri, car, gil, gra, jin, per, wal, rundec = -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1
        for i in gopdata:
            polls = i["pollster"]
            notend = i["end_date"]
            notstart = i["start_date"]
            method = i["method"]
            #logging.error(str(polls)+" "+str(notend))
            start = datetime.strptime(notstart, '%Y-%m-%d')
            end = datetime.strptime(notend, '%Y-%m-%d')
            lastupdated = datetime.strptime(i["last_updated"], '%Y-%m-%dT%H:%M:%S.%fZ')
            if (lastupdated <= topdategop):
                #logging.error('breaking at '+str(polls))
                breakvar = True
                break
            sourceurl = i["source"]
            if (str(sourceurl) == ''):
                sourceurl = 'None'
            for j in i["questions"]:
                tru, sant, rub, pau, pat, kas, bus, huc, fio, cru, chri, car, gil, gra, jin, per, wal, rundec = -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1
                if (str(j["topic"]) == "2016-president-gop-primary" and str(j["chart"]) == '2016-national-gop-primary'):
                    logging.error(str(j['chart']))
                    pop = j["subpopulations"][0]["observations"]
                    if (str(pop) == 'None'):
                        pop = -1
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
                    entry = NationalRepublicanPrimary(pollster=polls, start_date=start, end_date=end, entry_date=lastupdated, popsize=pop, poptype=poptype, mode=method, trump=tru, cruz=cru, rubio=rub, kasich=kas, carson=car, bush=bus, christie=chri, paul=pau, fiorina=fio, huckabee=huc, santorum=sant, gilmore=gil, gram=gra, jindal=jin, pataki=pat, perry=per, walker=wal, undecided=rundec, url=sourceurl)
                    entry.put()
                    #logging.error('put entry: '+" "+str(polls))
        if (breakvar == True):
            break
        sleep(1.00)

    #this for loop goes through each page in the api database, starting at page = 1 (most recent) and going to the end (earliest)
    tempdemdate = GqlQuery("SELECT * FROM NationalDemocraticPrimary ORDER BY entry_date DESC").get()
    try:
        topdatedem = tempdemdate.entry_date       
    except:
        topdatedem = datetime.min 
    #logging.error(str(topdatedem))
    breakvar = False
    for x in range(1,100):
        logging.error('DEM page: '+str(x))
        bill_method = 'sort=updated&page=%d&' % (x)
        try:
            dem = urllib2.urlopen(dem_url % bill_method)
        except:
            logging.error('failed of end of things dem')
        demo = dem.read()
        demdata = json.loads(demo)
        cli, sand, omal, cha, web, bid, dundec = -1, -1, -1, -1, -1, -1, -1
        for i in demdata:
            polls = i["pollster"]
            notend = i["end_date"]
            notstart = i["start_date"]
            #logging.error(str(polls)+" "+str(notend))
            start = datetime.strptime(notstart, '%Y-%m-%d')
            end = datetime.strptime(notend, '%Y-%m-%d')
            lastupdated = datetime.strptime(i["last_updated"], '%Y-%m-%dT%H:%M:%S.%fZ')
            if (lastupdated <= topdatedem):
                #logging.error('breaking at '+str(polls))
                breakvar = True
                break
            method = i["method"]
            sourceurl = i["source"]
            if (str(sourceurl) == ''):
                sourceurl = 'None'
            for j in i["questions"]:
                cli, sand, omal, cha, web, bid, dundec = -1, -1, -1, -1, -1, -1, -1
                if (str(j["topic"]) == "2016-president-dem-primary" and str(j["chart"]) == '2016-national-democratic-primary'):
                    logging.error(str(j['chart']))
                    pop = j["subpopulations"][0]["observations"]
                    if (str(pop) == 'None'):
                        pop = -1
                    poptype = j["subpopulations"][0]["name"]
                    for k in j["subpopulations"][0]["responses"]:
                        if (k["choice"] == "Clinton"):
                            cli = int(k["value"])
                        if (k["choice"] == "Sanders"):
                            sand = int(k["value"])
                        if (k["choice"] == "O'Malley"):
                            omal = int(k["value"])
                    entry = NationalDemocraticPrimary(pollster=polls, start_date=start, end_date=end, entry_date=lastupdated, popsize=pop, poptype=poptype, mode=method, hill=cli, sanders=sand, omalley=omal, chafee=cha, webb=web, biden=bid, undecided=dundec, url=sourceurl)
                    entry.put()
                    #logging.error('put entry: '+" "+str(polls))
        if (breakvar == True):
            break
        sleep(1.00)

def getStatePolls():
    #make api call to get most recent batch of poll data
    #logging.error('whats up')
    #compare api data to most recent data from datastore IF !=, append db with data
    #(datastore classes are (NationalDemocraticPrimary, NationalRepuclicanPrimary)

    #return two csv strings of polling data formatted for graph only

    dem_url = 'http://elections.huffingtonpost.com/pollster/api/polls.json?%stopic=2016-president-dem-primary'
    gop_url = 'http://elections.huffingtonpost.com/pollster/api/polls.json?%stopic=2016-president-gop-primary'
    tempgopdate = GqlQuery("SELECT * FROM StateRepublicanPrimary ORDER BY entry_date DESC").get()
    try:
        topdategop = tempgopdate.entry_date
    except:
        topdategop = datetime.min
    breakvar = False
    #this for loop goes through each page in the api database, starting at page = 1 (most recent) and going to the end (earliest)
    for x in range(1,100):
        logging.error('GOP page: '+str(x))
        bill_method = 'sort=updated&page=%d&' % (x)
        try:
            gop = urllib2.urlopen(gop_url % bill_method)
        except:
            logging.error('failed or end of things gop')
        repu = gop.read()
        gopdata = json.loads(repu)
        tru, sant, rub, pau, pat, kas, bus, huc, fio, cru, chri, car, gil, gra, jin, per, wal, rundec = -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1
        for i in gopdata:
            polls = i["pollster"]
            notend = i["end_date"]
            notstart = i["start_date"]
            method = i["method"]
            #logging.error(str(polls)+" "+str(notend))
            start = datetime.strptime(notstart, '%Y-%m-%d')
            end = datetime.strptime(notend, '%Y-%m-%d')
            lastupdated = datetime.strptime(i["last_updated"], '%Y-%m-%dT%H:%M:%S.%fZ')
            if (lastupdated <= topdategop):
                #logging.error('breaking at '+str(polls))
                breakvar = True
                break
            sourceurl = i["source"]
            if (str(sourceurl) == ''):
                sourceurl = 'None'
            for j in i["questions"]:
                tru, sant, rub, pau, pat, kas, bus, huc, fio, cru, chri, car, gil, gra, jin, per, wal, rundec = -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1
                #logging.error(str(j["topic"])+' '+str(j["chart"]))
                if (str(j["topic"]) == "2016-president-gop-primary" and str(j["chart"]) != '2016-national-gop-primary'):
                    state = str(j["chart"]).split('-')[1]
                    if state == 'new' or state == 'north' or state == 'south' or state == 'west' or state == 'rhode':
                        state += '-'+str(j["chart"]).split('-')[2]
                    logging.error(state)
                    pop = j["subpopulations"][0]["observations"]
                    if (str(pop) == 'None'):
                        pop = -1
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
                    entry = StateRepublicanPrimary(state=state, pollster=polls, start_date=start, end_date=end, entry_date=lastupdated, popsize=pop, poptype=poptype, mode=method, trump=tru, cruz=cru, rubio=rub, kasich=kas, carson=car, bush=bus, christie=chri, paul=pau, fiorina=fio, huckabee=huc, santorum=sant, gilmore=gil, gram=gra, jindal=jin, pataki=pat, perry=per, walker=wal, undecided=rundec, url=sourceurl)
                    entry.put()
                    #logging.error('put entry: '+" "+str(polls))
        if (breakvar == True):
            break
        sleep(1.00)

    #this for loop goes through each page in the api database, starting at page = 1 (most recent) and going to the end (earliest)
    tempdemdate = GqlQuery("SELECT * FROM StateDemocraticPrimary ORDER BY entry_date DESC").get()
    try:
        topdatedem = tempdemdate.entry_date       
    except:
        topdatedem = datetime.min 
    breakvar = False
    for x in range(1,100):
        logging.error('DEM page: '+str(x))
        bill_method = 'sort=updated&page=%d&' % (x)
        try:
            dem = urllib2.urlopen(dem_url % bill_method)
        except:
            logging.error('failed of end of things dem')
        demo = dem.read()
        demdata = json.loads(demo)
        cli, sand, omal, cha, web, bid, dundec = -1, -1, -1, -1, -1, -1, -1
        for i in demdata:
            polls = i["pollster"]
            notend = i["end_date"]
            notstart = i["start_date"]
            start = datetime.strptime(notstart, '%Y-%m-%d')
            end = datetime.strptime(notend, '%Y-%m-%d')
            lastupdated = datetime.strptime(i["last_updated"], '%Y-%m-%dT%H:%M:%S.%fZ')
            if (lastupdated <= topdatedem):
                breakvar = True
                break
            method = i["method"]
            sourceurl = i["source"]
            if (str(sourceurl) == ''):
                sourceurl = 'None'
            for j in i["questions"]:
                cli, sand, omal, cha, web, bid, dundec = -1, -1, -1, -1, -1, -1, -1
                #logging.error(str(j["topic"])+' '+str(j["chart"]))
                if (str(j["topic"]) == "2016-president-dem-primary" and str(j["chart"]) != '2016-national-democratic-primary'):
                    state = str(j["chart"]).split('-')[1]
                    if state == 'new' or state == 'north' or state == 'south' or state == 'west' or state == 'rhode':
                        state += '-'+str(j["chart"]).split('-')[2]
                    logging.error(state)
                    pop = j["subpopulations"][0]["observations"]
                    if (str(pop) == 'None'):
                        pop = -1
                    poptype = j["subpopulations"][0]["name"]
                    for k in j["subpopulations"][0]["responses"]:
                        if (k["choice"] == "Clinton"):
                            cli = int(k["value"])
                        if (k["choice"] == "Sanders"):
                            sand = int(k["value"])
                        if (k["choice"] == "O'Malley"):
                            omal = int(k["value"])
                    entry = StateDemocraticPrimary(state=state, pollster=polls, start_date=start, end_date=end, entry_date=lastupdated, popsize=pop, poptype=poptype, mode=method, hill=cli, sanders=sand, omalley=omal, chafee=cha, webb=web, biden=bid, undecided=dundec, url=sourceurl)
                    entry.put()
                    #logging.error('put entry: '+" "+str(polls))
        if (breakvar == True):
            break
        sleep(1.00)