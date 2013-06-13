#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import webapp2
import cgi
import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PWD_RE = re.compile(r"^.{3,20}$")
EML_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

ERROR_U="Please enter a valid username"
ERROR_P="Please enter a valid password"
ERROR_V="Passwords do not match. Please try again"
ERROR_E="Please enter a valid email address"

form = """
<form method="post">
	<textarea name="text" action="/rot13">%(msg)s</textarea>
	<br>
	<input type="submit">
</form>	

"""

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

welcome_msg = """
Welcome, %(user)s!
"""

def valid_username(self, username):
    return False
    	#return USER_RE.match(username)	


    



class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello, Udacity!')

class rot13(webapp2.RequestHandler):


	def rot13(self, texto=""):
		txt = list(texto)
		new_txt = ''
		for word in txt:
			if ((ord(word) >= 65 and ord(word) <= 77) or (ord(word) >= 97 and ord(word)<=109)):
				new_txt = new_txt + chr(ord(word)+13)
			elif ((ord(word) > 77 and ord(word) <= 90) or (ord(word) > 109 and ord(word)<=122)):
				new_txt = new_txt + chr(ord(word)-13)
			else: new_txt = new_txt + word
		new_txt = str(cgi.escape(new_txt, quote = True))
		return new_txt

	def write_form(self, msg=""):
		self.response.out.write(form % {"msg": msg})

	def get(self):
		self.write_form()
		

	def post(self):
		msg = self.request.get('text')
		msg2 = self.rot13(msg)
		self.write_form(msg2)

class signup(webapp2.RequestHandler):

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

		if not self.valid_password(pwd):
			errorp2 = ERROR_P

		if not self.valid_verify(pwd, verify):
			errorv2 = ERROR_V
 
		if not self.valid_email(email):
			errore2 = ERROR_E
			email2 = ""
		 
		if (self.valid_username(user) and self.valid_password(pwd) and self.valid_verify(pwd, verify) and self.valid_email(email)):
				self.redirect('/welcome?username=' + user)
		else: 
			self.write_form2(erroru2, errorp2, errore2, user2, email2, errorv2)		

		#validate username
	
class welcome(webapp2.RequestHandler):
	def get(self):
		
		user = str(self.request.get('username'))
		self.response.out.write(welcome_msg % {"user": user})
	"""	
		def valid_username(self, username):
			return USER_RE.match(username)

		def get(self):
			username = self.request.get('username')
        	if self.valid_username(username):
        		self.render('welcome.html', username = username)
        	else:
        		self.redirect('/signup')
    """    		
        			

  	
	




app = webapp2.WSGIApplication([('/', MainHandler),('/rot13', rot13), ('/signup', signup), ('/welcome', welcome)], debug=True)
