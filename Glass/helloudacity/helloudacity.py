import webapp2

form = """
<textarea form method="post" action="/testform">
	<input type="text" value="%(input)s" name="q">
	<input type="submit">
</form>
""" 

class MainPage(webapp2.RequestHandler):

    def get(self):
		self.response.out.write(form % {'input':"input text"})

class TestHandler(webapp2.RequestHandler):
	def post(self):
		self.response.headers['Content-Type'] = 'text/plain'
		q = self.request.get("q")
		#applying the cipher

		self.response.out.write(q)

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/testform', TestHandler)
], debug=True)
