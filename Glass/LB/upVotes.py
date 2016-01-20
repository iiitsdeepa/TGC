def process_votes_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        temp = row_str.split(',')
        entry = Votes(bill_id=temp[0],rid=temp[1],congress=temp[2],voted_at=temp[3],vote_type=temp[4],roll_type=temp[5],question=temp[6],required=temp[7],result=temp[8],source=temp[9],breakdown=temp[10],break_gop=temp[11],break_dem=temp[12],break_ind=temp[13])
        entry.put()

def process_ind_votes_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        temp = row_str.split(',')
        entry = Ind_Votes(bill_id=temp[0], bioguide_id=temp[1], vote=temp[2])
        entry.put()

class Votes(db.Model):
    bill_id = db.StringProperty(required = True)
    rid = db.StringProperty(required = True)
    congress = db.StringProperty(required = True)
    voted_at = db.StringProperty(required = True)
    vote_type = db.StringProperty(required = True)
    roll_type = db.StringProperty(required = True)
    question = db.StringProperty(required = True)
    required = db.StringProperty(required = True)
    result = db.StringProperty(required = True)
    source = db.StringProperty(required = True)
    breakdown = db.StringProperty(required = True)
    break_gop = db.StringProperty(required = True)
    break_dem = db.StringProperty(required = True)
    break_ind = db.StringProperty(required = True)

class Ind_Votes(db.Model):
    bill_id = db.StringProperty(required = True)
    bioguide_id = db.StringProperty(required = True)
    vote = db.StringProperty(required = True)

#bid,rid,congress,voted_at,vote_type,roll_type,question,required,result,source,breakdown,break_gop,break_dem,break_ind
#bid, bioguide_id, vote