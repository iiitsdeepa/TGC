def process_month_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        time, m1, m2, imp, exp, bal, fedfun, unemp, labpart, numemp, numunemp, weeksunemp, cpi, cpichng, cpiless, cpilesschng = row_str.split(',')
        entry = Monthly(timeperiod=time, m1supply=m1, m2supply=m2, imports=imp, exports=exp, fedfunds = fedfund, unemprate=unemp, laborforcepart=labpart, numemp=numemp, numunemp=numunemp, weeksunemp=weeksunemp, monthcpi=cpi, monthcpichng=cpichng, monthcpiless=cpiless, monthcpilesschng=cpilesschng)
        entry.put()

def process_quarter_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        time, gdp, gdpproc = row_str.split(',')
        entry = Quarterly(timeperiod=time, gdp=gdp, gdpchng=gdproc)
        entry.put()
		
def process_year_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        time, tpn4y, tpn4yc, tp4y, tp4yc, tp2y, tp2yc, apn4y, apn4yc, ap4y, ap4yc, samsize, il20, il40, il60, il80, il95, al20, al40, al60, al80, al100, alt5, ml20, ml40, ml60, ml80, ml100, mlt5, rev, spend, surdef, socsurdef, usps, total, pubdebt, perrev, perspend, persurdef, perpubdebt, incometax, paytax, corpinctax, excisetax, estatetax, custom, misctax, discsp, mansp, manoff, netint, defen, nondefen, socsp, medicare, medicaid, incsec, otherret, other = row_str.split(',')
        entry = Yearly(timeperiod=time, tutprinon4yr=tpn4y, tutprinon4yrchng=tpn4yc, tutpub4yr=tp4y, tutpub4yrchng=tp4yc, tutpub2yr=tp2y, tutpub2yrchng=tp2yc, allprinon4yr=apn4y, allprinon4yrchng=apn4yc, allpub4yr=ap4y, allpub4yrchng=ap4yc, samsize=samsize, il20=il20, il40=il40, il60=il60, il80=il80, il95=il95, al20=al20, al40=al40, al60=al60, al80=al80, al100=al100, alt5=alt5, ml20=ml20, ml40=ml40, ml60=ml60, ml80=ml80, ml100=ml100, mlt5=mlt5, revenue=rev, spending=spend, surdef=surdef, socialsecsurdef=socsurdef, usps=usps, total=total, pubdebt=pubdebt, perrev=perrev, perspend=perspend, persurdef=persurdef, perpubdebt=perpubdebt, incometax=intometax, payrolltax=paytax, corpincometax=corpinctax, excisetax=excisetax, estatetax=estatetax, customsduties=custom, misctax=misctax, discspend=discsp, manspend=mansp, mandoffset=manoff, netinterest=netint, defense=defen, nondefense=nondefen, socialsecsp=socsp, medicare=medicare, medicaid=medicaid, incomesec=incsec, otherretdis=otherret, other=other)
        entry.put()
		
class Monthly(db.Model):
    timeperiod = db.StringProperty(required = True)
    m1supply = db.StringProperty(required = True)
    m2supply = db.StringProperty(required = True)
    imports = db.StringProperty(required = True)
    exports = db.StringProperty(required = True)
    fedfunds = db.StringProperty(required = True)
    unemprate = db.StringProperty(required = True)
    laborforcepart = db.StringProperty(required = True)
    numemp = db.StringProperty(required = True)
    numunemp = db.StringProperty(required = True)
    weeksunemp = db.StringProperty(required = True)
    monthcpi = db.StringProperty(required = True)
    monthcpichng = db.StringProperty(required = True)
    monthcpiless = db.StringProperty(required = True)
	monthcpilesschng = db.StringProperty(required = True)

class Quarterly(db.Model):
    timeperiod = db.StringProperty(required = True)
    gdp = db.StringProperty(required = True)
    gdpchng = db.StringProperty(required = True)
	
class Yearly(db.Model):
    timeperiod = db.StringProperty(required = True)
    tutprinon4yr = db.StringProperty(required = True)
	tutprinon4yrchng = db.StringProperty(required = True)
	tutpub4yr = db.StringProperty(required = True)
    tutpub4yrchng = db.StringProperty(required = True)
    tutpub2yr = db.StringProperty(required = True)
	tutpub2yrchng = db.StringProperty(required = True)
    allprinon4yr = db.StringProperty(required = True)
    allprinon4yrchng = db.StringProperty(required = True)
	allpub4yr = db.StringProperty(required = True)
    allpub4yrchng = db.StringProperty(required = True)
    samsize = db.StringProperty(required = True)
	il20 = db.StringProperty(required = True)
    il40 = db.StringProperty(required = True)
    il60 = db.StringProperty(required = True)
	il80 = db.StringProperty(required = True)
    il95 = db.StringProperty(required = True)
    al20 = db.StringProperty(required = True)
	al40 = db.StringProperty(required = True)
    al60 = db.StringProperty(required = True)
    al80 = db.StringProperty(required = True)
	al100 = db.StringProperty(required = True)
    alt5 = db.StringProperty(required = True)
    ml20 = db.StringProperty(required = True)
	ml40 = db.StringProperty(required = True)
    ml60 = db.StringProperty(required = True)
    ml80 = db.StringProperty(required = True)
	ml100 = db.StringProperty(required = True)
    mlt5 = db.StringProperty(required = True)
    revenue = db.StringProperty(required = True)
	spending = db.StringProperty(required = True)
    surdef = db.StringProperty(required = True)
    socialsecsurdef = db.StringProperty(required = True)
	usps = db.StringProperty(required = True)
    total = db.StringProperty(required = True)
    pubdebt = db.StringProperty(required = True)
	perrev = db.StringProperty(required = True)
    perspend = db.StringProperty(required = True)
    persurdef = db.StringProperty(required = True)
	perpubdebt = db.StringProperty(required = True)
    incometax = db.StringProperty(required = True)
    payrolltax = db.StringProperty(required = True)
	corpincometax = db.StringProperty(required = True)
    excisetax = db.StringProperty(required = True)
    estatetax = db.StringProperty(required = True)
	customsduties = db.StringProperty(required = True)
    misctax = db.StringProperty(required = True)
    discspend = db.StringProperty(required = True)
	mandspend = db.StringProperty(required = True)
    mandoffset = db.StringProperty(required = True)
    netinterest = db.StringProperty(required = True)
	defense = db.StringProperty(required = True)
    nondefense = db.StringProperty(required = True)
    socialsecsp = db.StringProperty(required = True)
	medicare = db.StringProperty(required = True)
    medicaid = db.StringProperty(required = True)
    incomesec = db.StringProperty(required = True)
	otherretdis = db.StringProperty(required = True)
    other = db.StringProperty(required = True)
		
class ExecutiveBaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    """def get_year_month(self, both):
        year, month = both.split('_')
        s = GqlQuery('SELECT senior_senator, junior_senator FROM State WHERE abbreviation=:1', state).get()
        q = District.all()
        q.filter('state', state)
        h = q.filter('num', 3).get()
        politicians = dict(ss=s.senior_senator, js=s.junior_senator, hr=h.representative)
        return politicians
"""
    def getMonth(self, both):
        #returns a dictionary with the basic info for the representative of district=dist
        #year, month = both.split('_')
        mon = GqlQuery('SELECT * FROM Monthly WHERE timeperiod=\'%s\'' %(both)).get()
        month = dict(montimeperiod = mon.timeperiod,
                monstate = mon.m1supply,
                mondistrict = mon.m2supply,
                monname = mon.imports,
                mongender = mon.exports,
                monparty = mon.fedfunds,
                monfyio = mon.unemprate,
                monlaborforcepart = mon.laborforcepart,
                monnumemp = mon.numemp,
                monnumunemp = mon.numunemp,
                monweeksunemp = mon.weeksunemp,
                moncpi = mon.monthcpi,
                moncpichng = mon.monthcpichng,
                moncpiless = mon.monthcpiless,
				moncpilesschng = mon.monthcpilesschng)
        return month

    def getQuarter(self, both):
        #returns a dictionary with the basic info for the representative of district=dist
        #year, month = both.split('_')
        quart = GqlQuery('SELECT * FROM Quarterly WHERE timeperiod=\'%s\'' %(both)).get()
        quarter = dict(quarttimeperiod = quart.timeperiod,
                quartgdp = quart.gdp,
                quartgdprateofchng = quart.gdpchng)
        return quarter
		
    def getYear(self, both):
        #returns a dictionary with the basic info for the representative of district=dist
        #year, month = both.split('_')
        yr = GqlQuery('SELECT * FROM Yearly WHERE timeperiod=\'%s\'' %(both)).get()
        year = dict(yrtimeperiod = yr.timeperiod,
                yrtuitionprivatenonprofit4year = yr.tutprinon4yr,
                yrtuitionprivatenonprofit4yearchange = yr.tutprinon4yrchng,
                yrtuitionpublic4year = yr.tutpub4yr,
                yrtuitionpublic4yearchange = yr.tutpub4yrchng,
                yrtuitionpublic2year = yr.tutpub2yr,
                yrtuitionpublic2yearchange = yr.tutpub2yrchng,
                yrallprivatenonprofit4year = yr.allprinon4yr,
                yrallprivatenonprofit4yearchange = yr.allprinon4yrchng,
                yrsamplesizeincome = yr.samsize,
                yrincomelevel20percent = yr.il20,
                yrincomelevel40percent = yr.il40,
                yrincomelevel60percent = yr.il60,
                yrincomelevel80percent = yr.il80,
                yrincomelevel95percent = yr.il95,
                yraggregateincomebottom20 = yr.al20,
                yraggregateincomesecond20 = yr.al40,
                yraggregateincomethird20 = yr.al60,
                yraggregateincomefourth20 = yr.al80,
                yraggregateincometop20 = yr.al100,
                yraggregateincometop5 = yr.alt5,
                yrmeanincomebottom20 = yr.ml20,
                yrmeanincomesecond20 = yr.ml40,
                yrmeanincomethird20 = yr.ml60,
                yrmeanincomefourth20 = yr.ml80,
                yrmeanincometop20 = yr.ml100,
                yrmeanincometop5 = yr.mlt5,
                yrtotalrevenue = yr.revenue,
                yrtotalspending = yr.spending,
                yrsurplusdeficit = yr.surdef,
                yrsocialsecsurplusdeficit = yr.socialsecsurdef,
                yruspssurplusdeficit = yr.usps,
                yrtotalsurplusdeficit = yr.total,
                yrpublichelddebt = yr.pubdebt,
                yrpercentgdprevenue = yr.perrev,
                yrpercentgdpspending = yr.perspend,
                yrpercentgdpsurplusdeficit = yr.persurdef,
                yrpercentgdppublichelddebt = yr.perpubdebt,
                yrincometaxrevenue = yr.incometax,
                yrpayrolltaxrevenue = yr.payrolltax,
                yrcorporateincometaxrevenue = yr.corpincometax,
                yrexcisttaxrevenue = yr.excisetax,
                yrestatetaxrevenue = yr.estatetax,
                yrcustomsdutiesrevenue = yr.customsduties,
                yrmisctaxrevenue = yr.misctax,
                yrdiscretionaryspending = yr.discspend,
                yrmandatoryspending = yr.mandspend,
                yrmandatoryspendingoffset = yr.mandoffset,
                yrnetinterestondebt = yr.netinterest,
                yrdefensediscspending = yr.defense,
                yrnondefensediscspending = yr.nondefense,
                yrsocialsecuritymandspending = yr.socialsecsp,
                yrmeidcaremandspending = yr.medicare,
                yrmedicaidmandspending = yr.medicaid,
                yrincomesecuritymandspending = yr.incomesec,
                yrotherretirementanddisabilitymandspending = yr.otherretdis,
                yrothermandspending = yr.other)
        return year