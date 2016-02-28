from basehandler import *

class VisualizationHandler(BaseHandler):
	def get(self):
		self.redirect('/')
	def post(self):
		vis = self.request.get('visualization')
		v = GqlQuery("SELECT * FROM Visualization WHERE name = :1", vis).get()
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

	cols = [
                {"id":"","label":"Candidate","pattern":"","type":"string"},
                {"id":"","label":"Delegates","pattern":"","type":"number"},
                {"id":"","role":"style","type":"string"}]

        data = dict(cols = cols,
                rows = rows)
        final = dict(title = v.title,
                xaxis = v.xaxis,
                yaxis = v.yaxis,
                element = v.element,
                data = data)
        logging.error(final)
        self.response.out.write(json.dumps(final))