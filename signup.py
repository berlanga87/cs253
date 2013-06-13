import os
import webapp2
import jinja2
import hashlib
import hmac
import cgi
import re

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)

SECRET = "quesito"
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PWD_RE = re.compile(r"^.{3,20}$")
EML_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

ERROR_U="Please enter a valid username"
ERROR_P="Please enter a valid password"
ERROR_V="Passwords do not match. Please try again"
ERROR_E="Please enter a valid email address"
form2 = """
Signup
<form method="post">
	Username<input type="text" name="username" value="%(user)s"><span style="color:red">%(erroru)s</span><br>
	Password<input type="password" name="password"><span style="color:red">%(errorp)s</span><br>
	Verify Password<input type="password" name="verify"><span style="color:red">%(errorv)s</span><br>
	Email (optional)<input type="text" name="email" value="%(email)s"><span style="color:red">%(errore)s</span><br>
	<input type="submit">	
</form>
"""

def hash_str(s):
	return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
	return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val

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



# user database
class User(db.Model):
	user = db.StringProperty(required = True)
	password = db.StringProperty(required = True)



class Signup(Handler):

	def valid_username(self, username):
		return USER_RE.match(username)	

	def valid_password(self, pwd):
		return PWD_RE.match(pwd)

	def valid_email(self, email):
		return EML_RE.match(email)

	def valid_verify(self, pwd, verify):
		if pwd == verify:
			return True	

	def write_form2(self, erroru="", errorp="", errore="", user="", email="", errorv=""):
		self.response.out.write(form2 % {"erroru": erroru, "errorp": errorp, "errore": errore, "user": user, "email":email,"errorv":errorv})

	def get(self):
		self.write_form2()

	def post(self):

		user = cgi.escape(self.request.get('username'), quote= True)	
		pwd = cgi.escape(self.request.get('password'), quote= True)
		verify = cgi.escape(self.request.get('verify'), quote= True)
		email = cgi.escape(self.request.get('email'), quote= True)

		erroru2 = ""
		errorp2 = ""
		errore2 = ""
		user2 =  user 
		email2 = email
		errorv2 = ""
		#4 conditions - valid username, valid password, verified = pwd, email is valid
		if not self.valid_username(user):
			erroru2 = ERROR_U
			user2 = ""
		# check if username exists in database	

		if not self.valid_password(pwd):
			errorp2 = ERROR_P

		if not self.valid_verify(pwd, verify):
			errorv2 = ERROR_V
 
		if not self.valid_email(email) or email != "":
			errore2 = ERROR_E
			email2 = ""
		 
		if (self.valid_username(user) and self.valid_password(pwd) and self.valid_verify(pwd, verify) and self.valid_email(email)):
				#set cookie
				self.redirect('/welcome')
		else: 
			self.write_form2(erroru2, errorp2, errore2, user2, email2, errorv2)		

class Login(Handler):
	def get(self):
		self.write_form2()	#validate username	

class Logout(Handler):
	def get(self):
		cookie = self.request.cookies.get('login')
		if cookie:
			self.response.headers.add_header('Set-Cookie', 'login=0')
		self.redirect('unit3/signup')

class Welcome(Handler):
	def get(self):
		#read cookie
		cookie_str = self.request.cookies.get('login')

		# if cookie exists render html with username
		if cookie_str:
			cookie_val = check_secure_val(cookie_str)
			if cookie_val:
				self.write("Welcome, %s" % user)
			else:
				self.redirect('/unit3/signup')
		#get username
		





app = webapp2.WSGIApplication([('/unit3/signup',Signup),('/unit3/login', Login),('/unit3/logout', Logout), ('/unit3/welcome', Welcome)], debug=True)