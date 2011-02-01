from google.appengine.api import urlfetch
import urllib2
import urllib
import base64

def tweet(message, city, state, country):
  login =  "ledsignrpi"
  password = "ledsign"
  chime = message + " - from " + city + ", " + state + ", " + country + " - http://led.chrjo.com"
  payload= {'status' : chime,  'source' : "AppEngine"}
  payload= urllib.urlencode(payload)
  base64string = base64.encodestring('%s:%s' % (login, password))[:-1]
  headers = {'Authorization': "Basic %s" % base64string} 
  url = "http://twitter.com/statuses/update.xml"
  result = urlfetch.fetch(url, payload=payload, method=urlfetch.POST, headers=headers)

