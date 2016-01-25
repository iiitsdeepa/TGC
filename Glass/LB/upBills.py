def process_bill_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
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
        if tempqueryrow is None:
            entry = Bill(bill_id=temp[0],official_title=temp[1],popular_title=temp[2],short_title=temp[3],nicknames=temp[4],url=temp[5],active=temp[6],vetoed=temp[7],enacted=temp[8],sponsor_id=temp[9], introduced=introduced, last_action=last_action, last_updated=datetime.today())
            entry.put()

class Bill(db.Model):
    bill_id = db.StringProperty(required = True)
    official_title = db.StringProperty(required = True)
    popular_title = db.StringProperty(required = True)
    short_title = db.StringProperty(required = True)
    nicknames = db.StringProperty(required = True)
    url = db.StringProperty(required = True)
    active = db.StringProperty(required = True)
    vetoed = db.StringProperty(required = True)
    enacted = db.StringProperty(required = True)
    sponsor_id = db.StringProperty(required = True)
    introduced = db.DateTimeProperty(required = True)
    last_action = db.DateTimeProperty(required = True)
    last_updated = db.DateTimeProperty(required = True)

