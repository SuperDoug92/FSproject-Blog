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
    # id=db.ID

class MainPage(Handler):
    def render_blog(self, title="", blog_entry="", error=""):
        entries = db.GqlQuery("SELECT * FROM Blog_entries ORDER BY created DESC limit 10")
        self.render("blog.html", title=title, blog_entry=blog_entry, error=error, entries=entries)

    def get(self):
        self.render_blog()

class PostPage(Handler):
    def render_post(post):
        self.render("entry.html", title=title, blog_entry=blog_entry, error=error, entry=post)

    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        self.render_post(post)

class NewPost(Handler):
    def render_blog_form(self, title="", blog_entry="", error=""):
        entries = db.GqlQuery("SELECT * FROM Blog_entries ORDER BY created DESC")
        self.render("new_entry.html", title=title, blog_entry=blog_entry, error=error, entries=entries)

    def get(self):
        self.render_blog_form()

    def post(self):
        title = self.request.get("title")
        blog_entry =self.request.get("blog_entry")

        if title and blog_entry:
            b = Blog_entries(title=title, blog_entry=blog_entry)
            obj = b.put()

            self.redirect("/blog/" + post_id)
        else:
            error = "A blog post need a title and a entry!"
            self.render_blog_form(title, blog_entry, error)

app = webapp2.WSGIApplication([('/blog', MainPage),('/blog/newpost', NewPost),(r'/blog/(\d+)', PostPage)], debug=True)
