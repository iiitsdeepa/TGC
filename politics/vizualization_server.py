from basehandler import *

class VisualizationHandler(BaseHandler):
    def barjson(self,vquery):
    	dataquery = GqlQuery(vquery.query)
        rows = []
        for d in dataquery:
            t1 = dict(vquery=d.name)
            t2 = dict(vquery=d.delegates)
            ts = dict(vquery=vquery.color)
            t3 = [t1,t2,ts]
            temp = dict(c=t3)
            #logging.error(d.name+' '+d.party)
            rows.append(temp)
        cols = [
                {"id":"","label":"Candidate","pattern":"","type":"string"},
                {"id":"","label":"Delegates","pattern":"","type":"number"},
                {"id":"","role":"style","type":"string"}
            ]
        data = dict(cols = cols,
                rows = rows)
        final = dict(title = vquery.title,
                xaxis = vquery.xaxis,
                yaxis = vquery.yaxis,
                element = vquery.element,
                data = data)
        logging.error(final)
        return(json.dumps(final))
    
    def get(self):
        self.redirect('/')

    def post(self):
        vis = self.request.get('visualization')
        v = GqlQuery("SELECT * FROM Visualization WHERE name = :1", vis).get()
        json = self.barjson(v)
        self.response.out.write(json)