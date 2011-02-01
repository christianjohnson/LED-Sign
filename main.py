import cgi
import tweet
import urllib2

from xml.dom import minidom
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.api import xmpp
from datetime import timedelta
from dblist import Messages

def parse(ip):
  url = "http://ipinfodb.com/ip_query.php?ip=" + ip + "&timezone=false"
  request = urllib2.Request(str(url))
  opener = urllib2.build_opener()
  try:
    result = opener.open(request).read()
  except urllib2.URLError, e:
    return
  city = "Houston"
  state = "Texas"
  country = "USA"
  lat = 37
  lon = -122
  dict ={}
  results = minidom.parseString(result)
  rootNode = results.firstChild
  dict['city'] = rootNode.childNodes[13].firstChild.data
  dict['state'] = rootNode.childNodes[11].firstChild.data
  dict['country'] = rootNode.childNodes[7].firstChild.data
  dict['lat'] = rootNode.childNodes[17].firstChild.data
  dict['lon'] = rootNode.childNodes[19].firstChild.data
  return dict

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write("""
    <html><head><title>Christian's LED Sign</title>
    <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>
    <link rel="alternate" title="RSS Feed" href="http://feeds.feedburner.com/ledsign" type="application/rss+xml"> 
    <link rel="stylesheet" type="text/css" href="css/style.css" />
    <script type="text/javascript" src="js/jquery.js"></script>
    <script type="text/javascript" src="js/main.js"></script>
    <script type="text/javascript">
     var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
     document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
    </script>
    <script type="text/javascript">
     try {
       var pageTracker = _gat._getTracker("UA-13296842-1");
       pageTracker._setDomainName("none");
       pageTracker._setAllowLinker(true);
       pageTracker._trackPageview();
     } catch(err) {}
    </script>
    </head><body onload="initialize()">
    <div align="right">
    <a href="http://feeds.feedburner.com/ledsign" title="Subscribe to my feed" rel="alternate" type="application/rss+xml"><img src="http://www.feedburner.com/fb/images/pub/feed-icon16x16.png" alt="" style="border:0"/></a>
    </div>
    <div class="title"><h1 class="title">Christian's LED Sign</h1>
    <h3 class="title">Text the sign at (802) 468-SIGN - <a 
href="http://www.twitter.com/ledsignrpi" target="_blank" style="color:white">Follow on Twitter</a> - GChat: ledsignmessage@appspot.com</h3></div>
    <div class="messageBox">
    <form action="/sign" method="post" style="margin-top:2%">
    <input type="text" name="content" maxLength="60" style="WIDTH: 400px;" /><input id="submit" type="submit" value="Message LED" />
    </form>
    </div>
    <div id="map_canvas"></div><div id="lcontainer">
    <ul id="mess"></ul></div></body></html>
    """)

class Guestbook(webapp.RequestHandler):
  def post(self):
    greeting = Messages()
    if users.get_current_user():
      greeting.author = users.get_current_user()
    try:
      greet = unicode(self.request.get('content').decode('utf-8'))
    except UnicodeEncodeError:
      greet = "I don't speaka your language!"
      self.response.out.write('<script type="text/javascript">window.location = "http://www.youtube.com/watch?v=DNT7uZf7lew"</script>')
      return
    if len(greet) < 1:
      greet = "I'm an Idiot!"
    greeting.content = greet[:60]

    greeting.ipaddr = str(self.request.remote_addr)
    '''ip_greets = db.GqlQuery("SELECT * FROM Messages ORDER BY date DESC LIMIT 1 WHERE ipaddr = '" + greeting.ipaddr + "'")
    for ip_greet in ip_greets:
        try:
            if ip_greet.blocktime >= (greeting.date.minutes - ip_greet.minutes):
                self.redirect('/')
            elif ip_greet.blocktime*2 >= (greeting.date.minutes - ip_greet.minutes):
                greeting.blocktime = ip_greet.blocktime * 2
            else:
                greeting.blocktime = 1
        except:
            greeting.blocktime = 1'''
    greeting.blocktime = 1
    greetings = db.GqlQuery("SELECT * FROM Messages ORDER BY date DESC LIMIT 20")
    found = False
    if greeting.ipaddr.startswith("128.113") or greeting.ipaddr.startswith("128.213") or greeting.ipaddr.startswith("129.161") or greeting.ipaddr.startswith("129.5"):
      greeting.city = "RPI"
      greeting.state = "New York"
      greeting.country = "United States"
      greeting.lat = 42.7495
      greeting.lon = -73.5951
    else:
      for greet in greetings:
        if greet.ipaddr==greeting.ipaddr:
          greeting.city = greet.city
          greeting.state = greet.state
          greeting.country = greet.country
          try:
            greeting.lat = float(greet.lat)
            greeting.lon = float(greet.lon)
          except TypeError:
            greeting.lat = 39
            greeting.lon = -70
          found = True
          break
        if found == False:
          location = parse(str(self.request.remote_addr))
          greeting.city = location['city']
          greeting.state = location['state']
          greeting.country = location['country']
          try:
            greeting.lat = float(location['lat'])
            greeting.lon = float(location['lon'])
          except TypeError:
            greeting.lat = 39
            greeting.lon = -70
    greeting.put()

    #Tweet the message
    tweet.tweet(greeting.content, greeting.city, greeting.state, greeting.country)

    #Google Talk to Christian
    user_address = ['yoandi@christianjohnson.org','christian@christianjohnson.org']
    msg = "New LED Sign Message: " + str(greeting.content) + " - from " + str(greeting.city)
    for user in user_address:
      chat_message_sent = False
      status_code = xmpp.send_message(user, msg)

    #mail.send_mail(sender="christian.ebayrules@gmail.com",to="890b2f84571f18885dfd117e53bfcd1914b323ea@mail2prowl.de",subject="LED",body=str(greeting.content))
    #mail.send_mail(sender="christian.ebayrules@gmail.com",to="8606800402@vtext.com",subject="LED",body=str(greeting.content))
    self.redirect('/')

class Message(webapp.RequestHandler):
  def get(self):
    greetings = db.GqlQuery("SELECT * FROM Messages ORDER BY date DESC LIMIT 1")
    for greeting in greetings:
      self.response.out.write(greeting.content)    

class Rss(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'application/rss+xml'
    str = """<?xml version="1.0"?><rss version="2.0">\n<channel>\n<title>Christian's LED Sign</title><link>http://led.chrjo.com</link><description>Christian's LED Sign</description>\n
"""
    self.response.out.write(str)
    greetings = db.GqlQuery("SELECT * FROM Messages ORDER BY date DESC LIMIT 50")
    for greeting in greetings:
      if greeting.city == None:
        greeting.city = 'Anytown'
      if greeting.state == None:
        greeting.state = 'Anystate'
      if greeting.country == None:
        greeting.country = 'United States'
      self.response.out.write('    <item>')
      #self.response.out.write('<title><a href="http://www.led.chrjo.com">Message from ' + greeting.city + ', ' + greeting.state + ', ' + greeting.country + '</a></title>')
      self.response.out.write('<title>Message from ' + greeting.city + ', ' + greeting.state + ', ' + greeting.country + '</title>')
      self.response.out.write('\n<link>http://led.chrjo.com/</link>\n')
      self.response.out.write('<description>' + greeting.content + '</description>')
      self.response.out.write('</item>\n')
    self.response.out.write('</channel>\n</rss>')

class XMPPHandler(webapp.RequestHandler):
  def post(self):
    message = xmpp.Message(self.request.POST)
    if message.body.lower() == 'latest':
      message.reply("Latest Message:")
      greetings = db.GqlQuery("SELECT * FROM Messages ORDER BY date DESC LIMIT 1")
      for greeting in greetings:
        message.reply(str(greeting.content))
    elif message.body[0:5].lower() == 'post:':
      greeting = Messages()
      greeting.content = str(message.body[6:66])
      greeting.city = 'Topeka'
      greeting.state = 'Kansas'
      greeting.country = 'USA'
      greeting.lat = 39.0536
      greeting.lon = -95.6775
      greeting.put()
      message.reply("Thanks for posting " + str(greeting.content) + "!")
      message.reply("Visit http://led.chrjo.com to see your message!")
      tweet.tweet(greeting.content, greeting.city, greeting.state, greeting.country)
    elif message.body.lower() == 'help':
      message.reply("Choose from the following commands:")
      message.reply("Latest - to show latest message")
      message.reply("Post: <message> - to post a  message to the sign")
      message.reply("Help - to show this guide")
      message.reply("Also visit http://led.chrjo.com for more features!")
    else:
      message.reply("Greetings!  Type help to show possible commands")


class RedirectRss(webapp.RequestHandler):
  def get(self):
    self.redirect('http://feeds.feedburner.com/ledsign')

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/sign', Guestbook),
                                      ('/text', Message),
                                      ('/rss',RedirectRss),
                                      ('/rssOrig',Rss),
                                      ('/_ah/xmpp/message/chat/', XMPPHandler)],
					debug=True)


def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
