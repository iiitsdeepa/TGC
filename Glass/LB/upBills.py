def process_bill_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        temp = row_str.split(',')
        bioidquery = GqlQuery("SELECT * FROM Bill WHERE bioguide_id = :1", temp[9])
        tempqueryrow = bioidquery.get()
        if tempqueryrow is None:
            entry = Bill(in_office=temp[0],party=temp[1],gender=temp[2],state=temp[3],state_name=temp[4],distrank=temp[5],chamber=temp[6],birthday=temp[7],fyio=int(temp[8]),bioguide_id=temp[9],crp_id=temp[10],fec_ids=temp[11],name=temp[12],phone=temp[13],website=temp[14],contact_form=temp[15],twitter_id=temp[16],youtube_id=temp[17],facebook_id=temp[18])
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

#bid,official_title,popular_title,short_title,nicknames,url,active,vetoed,enacted,sponsor
