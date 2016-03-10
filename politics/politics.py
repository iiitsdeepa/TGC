from updatevotes import *
from updatebills import *
from updatepolls import *
from updatecosponsors import *
import databaseclasses
from csvprocessing import *
from basehandler import *
from visualization_server import *
from caching import *

#from oauth2client.client import flow_from_clientsecrets
#from oauth2client.client import FlowExchangeError
#import httplib2
#import requests

#--------------------------Pages----------------------------------------
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
        #process_nationalpolls(info, 'D')
        #process_politician_csv(info)
        #process_politician_stats(info)
        #process_candidate_csv(info)
        process_visualization_csv(info)
        #process_votes_csv(info)
        #process_ind_votes_csv(info)
        #process_bill_csv(info)
        #process_cosponsor_csv(info)
        self.redirect("/")

class Landing(BaseHandler):
    def get(self):
        self.render("landing.html")
    def post(self):
        self.render('landing.html')

class Home(BaseHandler):
    def get(self):
        self.render('landing.html')

class Election(BaseHandler):
    def get_primary_info(self):
        pinfo = GqlQuery('SELECT * FROM State ORDER BY name').get().all()
        ret = []
        for p in pinfo:
            t = dict(name = p.name,
                abbreviation = p.abbreviation,
                gedelegates = p.ge_delegates,
                ptype = p.primary_type,
                ddate = p.D_primary_date,
                ddelegates = p.D_delegates,
                dpledged = p.D_pledged,
                dsuper = p.D_super,
                rdate = p.R_primary_date,
                rdelegates = p.R_delegates,
                notes = p.primary_notes,
                rlink = p.registration_link)
            ret.append(t)
        return ret

    def get(self):
        pinfo = self.get_primary_info()
        self.render('election.html',pinfo=pinfo)

class Mreps(BaseHandler):
    def get(self):
        district = self.request.get('district')
        userstats = self.request.get('stats')
        statlist = ['Party Loyalty','Legislative Index','Bills Sponsored','Bills Cosponsored','% of Votes Missed','Number of Bills Enacted','Performance']
        basicstats = '1,2,3,5,7'
        if valid_district(district):
            if userstats:
                params = self.pullReps(district, statlist, userstats)
                self.render('mreps.html',PAGESTATE='found-district', **params)
            else:
                params = self.pullReps(district, statlist, basicstats)
                self.render('mreps.html',PAGESTATE='found-district', **params)
        elif userstats:
            params = self.getBig2(statlist, userstats)
            self.render('mreps.html', **params)
        else:
            params = self.getBig2(statlist, basicstats)
            self.render('mreps.html', **params)

    def post(self):
        statlist = ['Party Loyalty','Legislative Index','Sponsored Bills','% of Votes Missed','Performance']
        issuelist = self.request.get('issuelist')
        district = self.request.get('district')
        address = self.request.get('address')
        lat = self.request.get('lat')
        lng = self.request.get('lng')
        if issuelist:
            logging.error('+++++++++++++++++++ HERE')
            logging.error(issuelist)
            params = self.getBig2(statlist)
            params['issuelist'] = issuelist
            self.render('mreps.html', issuelist=issuelist, **params)
        elif lat and lng:
            district = self.latlngToDistrict(lat, lng)
            logging.error(district)
            self.write(district)
        elif address:
            district = self.address_to_district(address)
            logging.error(district)
            self.write(district)
        else:
            params = self.getBig2(statlist)
            logging.error(params)
            self.render('mreps.html', **params)

class News(BaseHandler):
    def get(self):
        self.render('news.html')

class Feedback(BaseHandler):
    def get(self):
        infos = self.read_secure_cookie('feedback_info')
        logging.error(str(infos))
        #if infos:
        #    info_str = str(infos)
        #    info = info_str.split('$$$')
        self.render('new-feedback.html')#, envir='checked=1')
    def post(self):
        oldcookie = self.read_secure_cookie('feedback_info')
        cookid = 0
        if oldcookie:
            temp = oldcookie.split('$$$')
            cookid = temp[0][10:]
        else:
            cookiedata = Cookie_Info(times_visit = 1, signup = False)
            cookiedata.put()
            cookkey = cookiedata.key()
            cookid = cookkey.id()
        activepart = self.request.get('activepart')
        listens = self.request.get('listens')
        easierpart = self.request.get('easierpart')
        issues = [self.request.get('environment'),
                  self.request.get('criminaljustice'),
                  self.request.get('health-care'),
                  self.request.get('privacy'),
                  self.request.get('education'),
                  self.request.get('campaigns'),
                  self.request.get('social-issues'),
                  self.request.get('guns'),
                  self.request.get('immigration'),
                  self.request.get('economy'),
                  self.request.get('foreign-policy'),
                  self.request.get('terrorism')]
        if activepart == '':
            activepart = -1
        if listens == '':
            listens = -1
        if easierpart == '':
            easierpart = -1
        for count in range(len(issues)):
            if (issues[count] == ''):
                issues[count] = 0
            else:
                issues[count] = 1
        feedradio = Feed_Radio_Buttons(cookie_id = int(cookid), listen_val = int(listens), active_val = int(activepart), easier_val = int(easierpart))
        feedradio.put()
        feedissues = Feed_Top_Issues(cookie_id = int(cookid), envir_sci = int(issues[0]), crim_just = int(issues[1]), health = int(issues[2]), privacy = int(issues[3]), edu = int(issues[4]), camp_fin_lobby = int(issues[5]), soc_issues = int(issues[6]), gun_cont = int(issues[7]), immig = int(issues[8]), econ = int(issues[9]), for_pol = int(issues[10]), terror = int(issues[11]))
        feedissues.put()
        cookietext = ('cookie_id='+str(cookid)+
                      '$$$listen_val='+str(listens)+
                      '$$$active_val='+str(activepart)+
                      '$$$easier_val='+str(easierpart))
        for i in range(len(issues)):
            cookietext += ('$$$issues-'+str(i)+'='+str(issues[i]))
        self.set_secure_cookie('feedback_info', cookietext)
        self.render('new-feedback.html')

class Sources(BaseHandler):
    def get(self):
        self.render('sources.html')
    def post(self):
        self.render('sources.html')

class About(BaseHandler):
    def get(self):
        self.render('teammembers.html')
    def post(self):
        self.render('about.html')

class NewsLetter(BaseHandler):
    def get(self):
        self.render('esf.html')

    def post(self):
        email = self.request.get('email')
        error_message = 'none'
        have_error = False
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

class Vprop(BaseHandler):
    def get(self):
        district = self.request.get('district')
        statlist = ['Party Loyalty','Legislative Index','Sponsored Bills','% of Votes Missed','Effectiveness']
        if valid_district(district):
            params = self.pullReps(district, statlist)
            logging.error(params)
            self.render('interactives.html',PAGESTATE='found-district', **params)
        else:
            logging.error('WHY T F IS THIS HAPPENING')
            params = self.getBig2(statlist)
            self.render('interactives.html', **params)

    def post(self):
        statlist = ['Party Loyalty','Legislative Index','Sponsored Bills','% of Votes Missed','Effectiveness']
        issuelist = self.request.get('issuelist')
        district = self.request.get('district')
        address = self.request.get('address')
        lat = self.request.get('lat')
        lng = self.request.get('lng')
        if issuelist:
            logging.error('+++++++++++++++++++ HERE')
            logging.error(issuelist)
            params = self.getBig2(statlist)
            params['issuelist'] = issuelist
            self.render('interactives.html', issuelist=issuelist, **params)
        elif lat and lng:
            district = self.latlngToDistrict(lat, lng)
            logging.error(district)
            self.write(district)
        else:
            params = self.getBig2(statlist)
            logging.error(params)
            self.render('interactives.html', **params)

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
        logging.error('')
        getStatePolls()
        logging.error('Votes')
        getVotesUpdate()
        logging.error('Bills')
        getBillsUpdate()
        logging.error('Setting Cache')
        updateCache()
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
        msg = 'Session expired, login again to continue browsing'
        if self.read_secure_cookie('sid'):
            secleft = self.is_session_active()
            if secleft >= 0:
                msg = 'Session cookie still active: '+str(secleft)+' seconds left.'
        self.render('login.html', error = msg)

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        u = User.login(username, password)
        if u:
            expr = datetime.now()+timedelta(seconds=SESSION_LENGTH)
            uid = u.key().id()
            sess = Session(userid = uid, expiration = expr)
            sess.put()
            self.login(sess, expr)
            self.redirect('/')
        else:
            msg = 'Invalid username or password'
            self.render('login.html', error = msg)

class PassReset(BaseHandler):
    def get(self):
        self.render('lostpassword.html')

    def post(self):
        username = self.request.get('username')
        databaseuser = GqlQuery("SELECT * FROM User WHERE username = :1", username).get()
        msg = ''
        try:
            email = databaseuser.email
            msg = 'An email will be sent to: '+str(email)
            random_bytes = os.urandom(102)
            token = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
            reset_key = token[:-2]
            databaseuser.reset_code = reset_key
            databaseuser.reset_expr = datetime.now() + timedelta(seconds=3600)
            databaseuser.put()
            reset_url = 'http://www.glasscapitol.com/emailreset?user=%s&key=%s' % (username, reset_key)
            logging.error(reset_url)
            sender_address = "glasscapitol.com Password Reset <glasscapitol@gmail.com>"
            subject = "Password Reset request - Glass Capitol"
            body = """
We have received a password reset request for the user: %s.
If you created this request, please click the link below to reset your password.

%s

If you did not create this request please check to see if your account has been accessed.
If this user is not you, please disregard and delete this email.

Thank you,
The Glass Capitol Team""" % (username, reset_url)
            mail.send_mail(sender_address, email, subject, body)
        except:
            msg = 'Incorrect username'
            reset_url = ''
        self.render('lostpassword.html', error = msg)

class EmailReset(BaseHandler):
    def get(self):
        username = self.request.get('user')
        key = self.request.get('key')
        emailuser = GqlQuery("SELECT * FROM User WHERE username = :1", username).get()
        try:
            expr_date = emailuser.reset_expr
            db_code = emailuser.reset_code
            expr_date = emailuser.reset_expr
            db_code = emailuser.reset_code
            if (key == ''):
                self.response.out.write('bad url or reset key expired, try password reset again')
            elif (key == db_code and expr_date > datetime.now()):
                self.render('emailpassreset.html', username = username)
            else:
                self.response.out.write('bad url or reset key expired, try password reset again')
        except:
            self.response.out.write('bad url or reset key expired, try password reset again')

    def post(self):
        newpass = self.request.get('password')
        passconf = self.request.get('passconf')
        username = self.request.get('user')
        emailuser = GqlQuery("SELECT * FROM User WHERE username = :1", username).get()
        try:
            if (newpass == passconf):
                if (len(newpass) < 8):
                    msg = 'Password must be at least 8 characters long'
                    self.render('emailpassreset.html', username = username, error = msg)
                else:
                    temp = User.changepass(username, newpass)
                    emailuser.pw_hash = str(temp.pw_hash)
                    emailuser.last_modified = datetime.now()
                    emailuser.reset_code = ''
                    emailuser.put()
                    self.render('successfulpasschange.html')
            else:
                msg = 'Passwords did not match, please try again'
                self.render('emailpassreset.html', username = username, error = msg)
        except:
            self.response.out.write('something screwed up')

class Logout(BaseHandler):
    def get(self):
        self.logout()
        self.redirect('/')

class CreateUser(BaseHandler):
    #correct url for this method is as follows: localhost:8080/createuser?username=alexh&email=alexh@gmail.com&password=lalalalala misspellings or blanks will be punished
    def get(self):
        username = self.request.get('username')
        email = self.request.get('email')
        password = self.request.get('password')
        if (username != '' and email != '' and password != ''):
            u = User.register(username, email, password, '', '')
            u.put()
            self.response.out.write('congrats it should have worked. Now go get a cookie')
        else:
            self.response.out.write('NOOOOOOOOO WHY MUST YOU KILL MEEEEEEEEE')

class Signup(BaseHandler):
    def get(self):
        self.render('presignup.html')

    def post(self):
        ty = self.request.get('type')
        if ty == 'keyform':
            key = self.request.get('key')
            if key == 'nextlevel':
                self.render('signup.html')
        elif ty == 'signupform':
            fname = self.request.get('firstname')
            lname = self.request.get('lastname')
            uname = self.request.get('username')
            email = self.request.get('email')
            password = self.request.get('password')
            passconf = self.request.get('passconf')
            if (password == passconf):
                existuser = GqlQuery("SELECT * FROM User WHERE username = :1", uname).get()
                existemail = GqlQuery("SELECT * FROM User WHERE email = :1", email).get()
                if (uname == ''):
                    msg = 'Username is a required field'
                    self.render('signup.html', error = msg, fname = fname, lname = lname, uname = uname, email = email)
                elif existuser is not None:
                    msg = 'Error creating user, information already exists'
                    self.render('signup.html', error = msg, fname = fname, lname = lname, uname = uname, email = email)
                elif (email == ''):
                    msg = 'Email is a required field'
                    self.render('signup.html', error = msg, fname = fname, lname = lname, uname = uname, email = email)
                elif existemail is not None:
                    msg = 'Error creating user, information already exists'
                    self.render('signup.html', error = msg, fname = fname, lname = lname, uname = uname, email = email)
                elif (len(password) < 8):
                    msg = 'Password must be at least 8 characters long'
                    self.render('signup.html', error = msg, fname = fname, lname = lname, uname = uname, email = email)
                else:
                    temp = User.register(uname, email, password, fname, lname)
                    temp.put()
                    feedcookie = self.read_secure_cookie('feedback_info')
                    if feedcookie:
                        tempcook = feedcookie.split('$$$')
                        cookid = tempcook[0][10:]
                        user_id = temp.key().id()
                        tempcook = Cookie_Info.get_by_id(int(cookid))
                        tempcook.user_id = user_id
                        tempcook.put()
                    logging.error('User created')
                    self.render('successfulsignup.html')
            else:
                msg = 'Passwords did not match, please try again'
                self.render('signup.html', error = msg, fname = fname, lname = lname, uname = uname, email = email)

class Onboarding(BaseHandler):
    def get(self):
        self.render('onboarding.html')

    def post(self):
        ty = self.request.get('type')
        if ty == 'issuelist':
            issuelist = self.request.get('list')
            self.render('ob-issuescroll.html')
        elif ty =='setview':
            uview = self.request.get('view')
            self.render('ob-select.html')

class Admin(BaseHandler):
    def get(self):
        fname = 'TGC'
        lname = 'Admin'
        uname = 'admin'
        email = 'glasscapitol@gmail.com'
        password = 'BTFUtgc925@'
        temp = User.register(uname, email, password, fname, lname)
        temp.put()
        self.login(temp)
        self.redirect('/')

class ESF(BaseHandler):
    def get(self):
        self.redirect('/home')

    def post(self):
        email = self.request.get('esfemail')
        error_message = 'none'
        have_error = False
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
    ('/', Home),
    ('/election', Election),
    ('/reps', Mreps),
    ('/news', News),
    ('/signup', Signup),
    ('/passwordreset', PassReset),
    ('/emailreset', EmailReset),
    ('/login', Login),
    ('/logout', Logout),
    ('/onboarding', Onboarding),
    ('/prop', Vprop),
    ('/feedback', Feedback),
    ('/about', About),
    ('/newsletter', NewsLetter),
    ('/sources', Sources),
    ('/pull/polldata', PollServer),
    ('/updateall', UpdateAll),
    ('/admin', Admin),
    ('/up', UploadHandler),
    ('/upload', Upload),
    #('/delete', bulkdelete),
    ('/marketing', Marketing),
    ('/esf', ESF),
    ('/vishandle', VisualizationHandler),
    ('/createuser', CreateUser)
], debug=True)
