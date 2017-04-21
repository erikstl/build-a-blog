import webapp2
import jinja2
import os

from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

#REFERENCE TO RENDER JINJA TEMPLATE
#t = jinja_env.get_template("add-confirmation.html")
#content = t.render(movie = new_movie_escaped)
#self.response.write(content)

class Blog(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class NewPost(webapp2.RequestHandler):
    def get(self):
        t = jinja_env.get_template("newpost.html")
        content = t.render()
        self.response.write(content)

    def post(self):
        title = self.request.get('title')
        body = self.request.get('body')
        error = ''

        if title and body:
            blog = Blog(title=title, body=body)
            blog.put()

            #ORM query and store in variable
            id = blog.key().id()

            self.redirect('/blog/%s' % id)
        else:
            error = 'You need a title and a body! This is a blog, after all!'
            t = jinja_env.get_template("newpost.html")
            content = t.render(error=error, title=title, body=body)
            self.response.write(content)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        t = jinja_env.get_template("blog.html")
        content = t.render(blogs=blogs)
        self.response.write(content)

class RecentPosts(webapp2.RequestHandler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        t = jinja_env.get_template("blog.html")
        content = t.render(blogs=blogs)
        self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post_id = Blog.get_by_id(int(id))
        title = post_id.title
        body = post_id.body

        t = jinja_env.get_template("post.html")
        content = t.render(title=title, body=body)
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', RecentPosts),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
