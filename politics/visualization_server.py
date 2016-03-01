from basehandler import *

class VisualizationHandler(BaseHandler):
    def barjson(self,v):
        cols = [
                {"id":"","label":v.xaxis,"pattern":"","type":"string"},
                {"id":"","label":v.yaxis,"pattern":"","type":"number"},
                {"id":"","role":"style","type":"string"}
            ]
        dataquery = GqlQuery(v.query)
        rows = []
        for d in dataquery:
            t1 = dict(v=d.name)
            t2 = dict(v=d.delegates)
            ts = dict(v=v.color)
            t3 = [t1,t2,ts]
            temp = dict(c=t3)
            #logging.error(d.name+' '+d.party)
            rows.append(temp)
        data = dict(cols = cols,
                rows = rows)
        final = dict(title = v.title,
                xaxis = v.xaxis,
                yaxis = v.yaxis,
                element = v.element,
                data = data)
        return(json.dumps(final))

    def makerow(self,d,names):
        retarray = [{"v":str(d.start_date)}]
        narray = names.split('$$$')
        for n in narray:
            t = dict(v=getattr(d,n))
            retarray.append(t)
        ret = dict(c=retarray)
        return ret

    def linejson(self,v):
        cols = [{"id":"","label":v.xaxis,"pattern":"","type":"string"}]
        col_array = v.query_columns.split('$$$')
        for c in col_array:
            t = {"id":"","label":c,"pattern":"","type":"number"}
            cols.append(t)
        cols.append({"id":"","role":"style","type":"string"})
        
        dataquery = GqlQuery(v.query)
        rows = []
        for d in dataquery:
            t = self.makerow(d,v.color)
            rows.append(t)
        data = dict(cols=cols,rows=rows)

        final = dict(title = v.title,
                xaxis = v.xaxis,
                yaxis = v.yaxis,
                element = v.element,
                data = data)
        return(json.dumps(final))


    def get(self):
        self.render('e1.html')

    def post(self):
        vis = self.request.get('visualization')
        v = GqlQuery("SELECT * FROM Visualization WHERE name = :1", vis).get()
        if v.vtype == 'bar':
            logging.error('bar')    
            j = self.barjson(v)
        elif v.vtype == 'line':
            logging.error('line')
            j = self.linejson(v)
        self.response.out.write(j)