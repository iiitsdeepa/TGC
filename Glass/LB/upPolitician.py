def process_politician_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        count = 0
        temp = row_str.split(',')
        bioidquery = GqlQuery("SELECT * FROM Politician WHERE bioguide_id = :1", temp[9])
        tempqueryrow = bioidquery.get()
        if tempqueryrow is None:
            count = 0
        else:
            count = 1
        if (count == 0):
            entry = Politician(in_office=temp[0],party=temp[1],gender=temp[2],state=temp[3],state_name=temp[4],distrank=temp[5],chamber=temp[6],birthday=temp[7],fyio=int(temp[8]),bioguide_id=temp[9],crp_id=temp[10],fec_ids=temp[11],name=temp[12],phone=temp[13],website=temp[14],contact_form=temp[15],twitter_id=temp[16],youtube_id=temp[17],facebook_id=temp[18])
            entry.put()

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

#in_office,party,gender,state,state_name,distrank,chamber,birthday,fyio,bioguide_id,crp_id,fec_ids,name,phone,website,contact_form,twitter_id,youtube_id,facebook_id