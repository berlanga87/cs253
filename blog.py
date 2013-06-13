import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)

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

#class to create an entity
class Post(db.Model):
	subject = db.StringProperty(required = True) #constraints are important
	content = db.TextProperty (required = True)
	created = db.DateTimeProperty(auto_now_add = True) #automatically adds current datetime

class Blog(Handler):
	def get(self):
		self.render_front()

	def render_front(self, subject="", content="", error=""):
		posts = db.GqlQuery("Select * from Post order by created")
		self.render("blog_front.html", posts = posts)
		

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)
	
class NewPost(Handler):
	def render_new(self, subject="", content="", error=""):
		self.render("new_post.html", subject=subject, content=content, error=error)

	def get(self):
		self.render_new()

	def post(self):
		
		subject = self.request.get("subject")
		content = self.request.get("content")

		if subject and content:
			p = Post(parent = blog_key(), subject = subject, content = content)
			p.put()
			self.redirect('/blog/%s' % str(p.key().id()))

		else:
			error = "we need both a subject and content!"
			self.render_new(subject, content, error)


class PostPage(Handler):
	def get(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		if not post:
			self.error(404)
			return

		self.render("permalink.html", post = post)

		

app = webapp2.WSGIApplication([('/blog/?', Blog),('/blog/([0-9]+)', PostPage),('/blog/newpost', NewPost)], debug=True)