import os
import webapp2
import jinja2
import re
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self,template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog_entries(db.Model):
    title = db.StringProperty(required=True)
    blog_entry = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_blog(self, title="", blog_entry="", error=""):
        entries = db.GqlQuery("SELECT * FROM Blog_entries ORDER BY created DESC limit 10")
        self.render("blog.html", title=title, blog_entry=blog_entry, error=error, entries=entries)

    def get(self):
        self.render_blog()

class PostPage(Handler):
    def render_post(self, post):
        self.render("entry.html", entry=post)

    def get(self, post_id):
        key = db.Key.from_path('Blog_entries', int(post_id))
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render_post(post)

class NewPost(Handler):
    def get(self):
        self.render("new_entry.html")

    def post(self):
        title = self.request.get("title")
        blog_entry =self.request.get("blog_entry")

        if title and blog_entry:
            b = Blog_entries(title=title, blog_entry=blog_entry)
            b.put()
            self.redirect('/blog/%s' % str(b.key().id()))
        else:
            error = "A blog post need a title and a entry!"
            self.render("new_entry.html", title=title, blog_entry=blog_entry, error=error)

class Welcome(Handler):
    def get(self):
        self.render("welcome.html")

    # def post(self):
    #     title = self.request.get("title")
    #     blog_entry =self.request.get("blog_entry")
    #
    #     if title and blog_entry:
    #         b = Blog_entries(title=title, blog_entry=blog_entry)
    #         b.put()
    #         self.redirect('/blog/%s' % str(b.key().id()))
    #     else:
    #         error = "A blog post need a title and a entry!"
    #         self.render_blog_form(title, blog_entry, error)

class SignUp(Handler):
    def get(self):
        self.render("sign_up.html")

    def validateUsername(username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return USER_RE.match(username)

    def validatePassword(password, verify):
        if password != verify:
            return False
        else:
            return True

    def validateEmail(email):
        EMAIL_RE = re.compile(r"^.{3,20}$")
        return EMAIL_RE.match(email)

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        usernameError = ''
        matchError = ''
        emailError = ''

        if validateUsername(username) = None:
            usernameError = 'invalid username'

        if not validatePassword(password, verify):
            matchError = 'Passwords do not match'

        if not validateEmail(email):
            emailError = 'Email not valid'

        if usernameError == ''and matchError == '' and emailError == '':
            # b = Blog_entries(title=title, blog_entry=blog_entry)
            # b.put()
            self.redirect('/welcome')
        else:
            self.render("sign_up.html", usernameError=usernameError, matchError=matchError, emailError=emailError)


app = webapp2.WSGIApplication([('/signup', SignUp),('/welcome', Welcome),('/blog/?', MainPage),('/blog/newpost', NewPost),('/blog/([0-9]+)', PostPage)], debug=True)
