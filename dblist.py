from google.appengine.ext import db

class Messages(db.Model):
  content = db.StringProperty(multiline=False)
  date = db.DateTimeProperty(auto_now_add=True)
  ipaddr = db.StringProperty(multiline=False)
  city = db.StringProperty(multiline=False)
  state = db.StringProperty(multiline=False)
  country = db.StringProperty(multiline=False)
  lat = db.FloatProperty()
  lon = db.FloatProperty()
  blocktime = db.IntegerProperty()
