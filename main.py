import wsgiref.handlers
import os

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

# Set the debug level
_DEBUG = True

class Solution(db.Model):
  submittime = db.DateTimeProperty(auto_now_add=True)
  title = db.StringProperty()
  problem = db.TextProperty()
  solution = db.TextProperty()
  name = db.StringProperty()
  moderated = db.BooleanProperty(default=False)

class Comment(db.Model):
  submittime = db.DateTimeProperty(auto_now_add=True)
  solutionid = db.StringProperty()
  details = db.TextProperty()
  name = db.StringProperty()
  upvotes = db.IntegerProperty(default=1)
  downvotes = db.IntegerProperty(default=0)
  moderated = db.BooleanProperty(default=False)

class BaseRequestHandler(webapp.RequestHandler):
  """Base request handler extends webapp.Request handler

     It defines the generate method, which renders a Django template
     in response to a web request
  """

  def generate(self, template_name, template_values={}):
    """Generate takes renders and HTML template along with values
       passed to that template

       Args:
         template_name: A string that represents the name of the HTML template
         template_values: A dictionary that associates objects with a string
           assigned to that object to call in the HTML template.  The defualt
           is an empty dictionary.
    """
    
    # Construct the path to the template
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 'templates', template_name)

    # Respond to the request by rendering the template
    self.response.out.write(template.render(path, template_values, debug=_DEBUG))

class HomePage(BaseRequestHandler):
  def get(self):
    solutions_query = Solution.all().order('-submittime')
    solutions = solutions_query.fetch(4)
    template_values = {
      "solutions" : solutions
    }
    self.generate('home.html', template_values)

class SolutionPage(BaseRequestHandler):
  def get(self):
    key_name = self.request.get('key')
    solution = db.get(db.Key(key_name))
    
    comment_query = Comment.all().order('-submittime').filter('solutionid =', key_name)
    comments = comment_query.fetch(50)
    
    if self.request.get("s"):
      showcongrats = bool(1)
    else:
      showcongrats = bool(0)
    
    #.reverse()
    template_values = {
      'ID' : key_name,
      'solution': solution,
      'comments':comments,
      'showcongrats': showcongrats
    }
    
    self.generate('solution.html', template_values)
    
    
class NewSolutionPage(BaseRequestHandler):
  def get(self):
    template_values = {
    }
    self.generate('newsolution.html', template_values)
  def post(self):    
    solution = Solution()
    solution.title = self.request.get("title")
    solution.problem = self.request.get("problem")
    solution.solution = self.request.get("solution")
    solution.name = self.request.get("name")
    
    key = solution.put()
    self.redirect('/solution?key='+ str(key) + "&s=1")
    
class CommentAction(BaseRequestHandler):
  def post(self):
    comment = Comment()
    comment.details = self.request.get("details")
    comment.solutionid = self.request.get("solutionid")
    comment.name = self.request.get("name")
  
    key = comment.put()
    self.redirect('/solution?key='+ str(comment.solutionid) + "&s=1")
    
def main():
  application = webapp.WSGIApplication(
  [('/', HomePage),
   ('/new', NewSolutionPage),
   ('/solution', SolutionPage),
   ('/comment', CommentAction)
  ],
                                       debug=_DEBUG)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
