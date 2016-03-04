from basehandler import *
from datetime import datetime, date, time, timedelta

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
            logging.error(t)
            retarray.append(t)
        ret = dict(c=retarray)
        return ret

    def natpolls(self,v):
        rows = []
        if self.request.get('length') != '' and self.request.get('length') != '':
            length = self.request.get('length')
            smooth = self.request.get('smooth')
        else:
            length = 30
            smooth = 10
        ultstartday = datetime.now() - timedelta(days=(int(smooth)+int(length)))
        ultendday = datetime.now()
        querystr = 'WHERE entry_date >= :1 AND entry_date <= :2'
        querystr = v.query%(querystr)
        query = GqlQuery(querystr, ultstartday, ultendday)
        masterquery = []
        for row in query:
            masterquery.append(row)
        for i in range(int(length)):
            startday = datetime.now() - timedelta(days=(i+int(smooth)))
            endday = datetime.now() - timedelta(days=i)
            tempquery = []
            for mq in masterquery:
                if mq.entry_date >= startday and mq.entry_date <= endday:
                    tempquery.append(mq)
            endday = endday.date()
            retarray = [{"v":str(endday)}]
            if v.name == 'dnpolls':
                average = [0,0]
            else:
                average = [0,0,0,0,0]
            count = 0
            for each in tempquery:
                narray = v.color.split('$$$')

                for i in range(len(narray)):
                    temp = getattr(each,narray[i])
                    average[i] += temp
                count += 1
            for j in range(len(average)):
                if average[j] < 0:
                    average[j] = 0;
            if v.name == 'dnpolls' and count != 0:
                average[0] = float(average[0])/float(count)
                average[1] = float(average[1])/float(count)
            elif count != 0:
                average[0] = float(average[0])/float(count)
                average[1] = float(average[1])/float(count)
                average[2] = float(average[2])/float(count)
                average[3] = float(average[3])/float(count)
                average[4] = float(average[4])/float(count)
            for each in average:
                t = dict(v=each)
                retarray.append(t)
            ret = dict(c=retarray)
            if i == 0:
                rows.append(ret)
            else:
                rows.insert(0,ret)
        return rows
                
    def linejson(self,v):
        cols = [{"id":"","label":v.xaxis,"pattern":"","type":"string"}]
        col_array = v.query_columns.split('$$$')
        for c in col_array:
            t = {"id":"","label":c,"pattern":"","type":"number"}
            cols.append(t)
        cols.append({"id":"","role":"style","type":"string"})
        
        rows = []
        if v.name == 'dnpolls' or v.name == 'rnpolls':
            rows = self.natpolls(v)
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
        v = GqlQuery("SELECT * FROM Visualization WHERE name = :1", vis).get()
        if v.vtype == 'bar':
            logging.error('bar')    
            j = self.barjson(v)
        elif v.vtype == 'line':
            logging.error('line')
            j = self.linejson(v)
        self.response.out.write(j)