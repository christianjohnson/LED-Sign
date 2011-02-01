#!/usr/bin/python2.4

import logging
from dblist import Messages
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import mail

class MailHandler(InboundMailHandler):
  def receive(self, message):
    bodies = message.bodies(content_type='text/plain')
    allBodies = "";
    for body in bodies:
      allBodies = allBodies + " " + body[1].decode()
      break
    allBodies = allBodies + " Length of AllBodies: " + str(len(allBodies))
    greeting = Messages()
    allBodies=allBodies[1:allBodies.find("--")]
    allBodies = allBodies.rstrip()
    greeting.content = allBodies
    greeting.ipaddr = '0.0.0.0'
    greeting.city = 'Cell Phone'
    greeting.state = 'Anytown'
    greeting.country = 'United States'
    greeting.blocktime = 1
    greeting.put()

application = webapp.WSGIApplication([MailHandler.mapping()], debug=True)
def main():
  run_wsgi_app(application)
if __name__ == "__main__":
  main()
