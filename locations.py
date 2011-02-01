import cgi
from google.appengine.ext import db
from dblist import Messages
from datetime import timedelta
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    try:
      limit = int(self.request.get('limit'))
    except ValueError:
      limit = 2
    greetings = db.GqlQuery("SELECT * FROM Messages ORDER BY date DESC LIMIT " + str(limit))
    messages = []
    for greeting in greetings:
      message = {}
      message['message'] = str(greeting.content)
      message['city'] = str(greeting.city)
      message['state'] = str(greeting.state)
      message['country'] = str(greeting.country)
      if greeting.lat != None:
        message['lat'] = greeting.lat
      else:
        message['lat'] = 30.107
      if greeting.lon != None:
        message['lon'] = greeting.lon
      else:
        message['lon'] = -71.894
      messages.append(message)
    self.response.out.write(messages)

application = webapp.WSGIApplication([('/locations', MainPage)],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
