from basehandler import *
from datetime import datetime, date, time, timedelta
from google.appengine.api import memcache
from caching import *

class VisualizationHandler(BaseHandler):
    def barjson(self,v):
        cols = [
                {"id":"","label":v.xaxis,"pattern":"","type":"string"},
                {"id":"","label":v.yaxis,"pattern":"","type":"number"},
                {"id":"","role":"style","type":"string"}
            ]
        if v.name == 'dpresults':
            cols = [
                    {"id":"","label":v.xaxis,"pattern":"","type":"string"},
                    {"id":"","label":v.yaxis,"pattern":"","type":"number"},
                    {"id":"","role":"style","type":"string"},
                    {"id":"","label":"Superdelegates","pattern":"","type":"number"},
                    {"id":"","role":"style","type":"string"}
                ]
        dataquery = GqlQuery(v.query)
        rows = []
        for d in dataquery:
            t4, t5 = 0, 0
            t1 = dict(v=d.name)
            t2 = dict(v=d.delegates)
            if v.name == 'dpresults':
                t4 = dict(v=d.superdelegates)
                t5 = dict(v='#809fff')
            ts = dict(v=v.color)
            t3 = [t1,t2,ts]
            if t4 is not int and t5 is not int:
                t3.append(t4)
                t3.append(t5)
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
            logging.error(t)
            retarray.append(t)
        ret = dict(c=retarray)
        return ret

    def statepolls(self,v,polltype):
        keytext = polltype[4:]
        rows = memcache.get(keytext)
        if rows is None:
            rows = setStatePolls(polltype, v.color)
            logging.error('memcache miss')
        else:
            logging.error('memcache hit')
        return rows

    def natpolls(self,v):
        if self.request.get('length') != '' and self.request.get('smooth') != '':
            length = self.request.get('length')
            smooth = self.request.get('smooth')
        else:
            length = 30
            smooth = 20
        keytext = v.name + str(smooth) + str(length)
        rows = memcache.get(keytext)
        if rows is None:
            rows = setNatPolls(length, smooth, v.name, v.color)
            logging.error('memcache miss')
        else:
            logging.error('memcache hit')
        return rows
                
    def linejson(self,v,polltype):
        cols = [{"id":"","label":v.xaxis,"pattern":"","type":"string"}]
        col_array = v.query_columns.split('$$$')
        for c in col_array:
            t = {"id":"","label":c,"pattern":"","type":"number"}
            cols.append(t)
        cols.append({"id":"","role":"style","type":"string"})
        
        rows = []
        logging.error(polltype)
        if v.name == 'dnpolls' or v.name == 'rnpolls':
            rows = self.natpolls(v)
        elif polltype[0:4] == '_st_':
            v.title = v.title % (codeToName(polltype[5:7]).capitalize())
            rows = self.statepolls(v, polltype)
        else:
            dataquery = GqlQuery(v.query)#%('ORDER BY start_date DESC LIMIT 10')
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

    def mapjson(self,v):
        a=1

    def get(self):
        self.render('e1.html')

    def post(self):
        vis = self.request.get('visualization')
        logging.error(vis)
        if vis[0:4] == '_st_':
            #vis = '_st_'+vis[4:5]+'%spolls'
            logging.error(str(vis))
            v = GqlQuery("SELECT * FROM Visualization WHERE name = :1", '_st_'+vis[4:5]+'%spolls').get()
        else:
            v = GqlQuery("SELECT * FROM Visualization WHERE name = :1", vis).get()
        if v.vtype == 'bar':
            logging.error('bar')    
            j = self.barjson(v)
        elif v.vtype == 'line':
            logging.error('line')
            j = self.linejson(v, vis)
        self.response.out.write(j)