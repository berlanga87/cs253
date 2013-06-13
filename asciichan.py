import os
import webapp2
import jinja2
from xml.dom import minidom


from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
IP_URL = "http://api.hostip.info/?ip=?"

CACHE = {}

def get_coords(ip):
	url = IP_URL + ip
	content = None
	try:
		content = urllib2.urlopen(url).read()
	except:
		return

	if content:
		d = minidom.parseString(content)
		coords = d.getElementsByTagName("gml:coordinates")
	if coords and coords[0].childNodes[0].nodeValue:
		lon, lat = coords[0].childNodes[0].nodeValue.split(',')
	return db.GeoPt(lat, lon)

def gmaps_img(points):
    url = GMAPS_URL
    for point in points:
        url += "&markers=" + str(point.lat) + "," + str(point.lon)
    return url

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

class Handler(webapp2.RequestHandler):
	def render_str(template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.response.out.write(render_str(template, **kw))

	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

class AsciiChan(Handler):
	def get(self):
		self.write(repr(get_coords(self.request.remote_addr)))
		self.render_front()

	def post(self):
		
		title = self.request.get("title")
		art = self.request.get("art")

		if title and art:
			a = Art(title = title, art = art)
			coords = get_coords(self.request.remote_addr)
			if coords:
				p.coords = coords
			a.put()
			self.redirect("/ascii")

		else:
			error = "we need both a title and art!"
			self.render_front(title, art, error)

	def render_front(self, title="", art="", error=""):
		arts = memcache.get('top')
		#find which arts have coords 
		img_url = None
		points = filter(None, (a.coords for a in arts))
		if points:
			img_url = gmaps_img(points)

		self.render("front.html", title=title, art=art, error=error)	
	
def top_arts(update = False):
	key = 'top'
	arts = mecache.get(key)

	if arts is None or update:
		arts = db.GqlQuery("Select * from Art order by created desc")
		arts = list(arts)
		memcache.set(key) = arts

#class to create an entity
#title->string, art -> Text and created->datetime
class Art(db.Model):
	title = db.StringProperty(required = True) #constraints are important
	art = db.TextProperty (required = True)
	created = db.DateTimeProperty(auto_now_add = True) #automatically adds current datetime
	coords = db.GeoPtProperty()

app = webapp2.WSGIApplication([('/ascii', AsciiChan)], debug=True)