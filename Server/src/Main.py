'''
Created on Apr 20, 2011

@author: Nathan V-C
'''

import cgi
import os
import logging

from django.utils import simplejson as json

from APIKeys import GoogleMapsAPIKey
from APIKeys import LastFMAPIKey

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api.urlfetch import fetch, InvalidURLError

class Event(db.Model):
	eventID = db.IntegerProperty()
	eventTitle = db.StringProperty()
	eventDescription = db.TextProperty()
	eventImageURLs =  db.ListProperty(db.Link)
	eventAttendance = db.IntegerProperty()
	eventReviews = db.IntegerProperty()
	eventTag = db.StringProperty()
	eventURL = db.LinkProperty()
	eventWebsite = db.LinkProperty()
	eventTickets = db.IntegerProperty()
	eventCancelled = db.IntegerProperty()
	
	venueID = db.IntegerProperty()
	venueName = db.StringProperty()
	venueURL = db.LinkProperty()
	venueWebsite = db.LinkProperty()
	venuePhoneNumber = db.PhoneNumberProperty()
	venueImageURLs =  db.ListProperty(db.Link)
	venueAddress = db.PostalAddressProperty()
	venueTimeZone = db.StringProperty()
	
	artists = db.StringListProperty()
	headliners = db.StringListProperty()
	
	tags = db.StringListProperty()
	
	geoPt = db.GeoPtProperty()
	date = db.DateTimeProperty()
	
	dateAdded = db.DateTimeProperty(auto_now_add=True)


class MainPage(webapp.RequestHandler):
	def get(self):
	#                greetings_query = Greeting.all().order('-date')
	#                greetings = greetings_query.fetch(10)
	#
	#                if users.get_current_user():
	#                        url = users.create_logout_url(self.request.uri)
	#                        url_linktext = 'Logout'
	#                else:
	#                        url = users.create_login_url(self.request.uri)
	#                        url_linktext = 'Login'
	
		#urlfetch.fetch("http://ws.audioscrobbler.com/2.0/",
		#               headers={"method": "geo.getevents",
		#                        ""})
		
		template_values = {'GoogleMapsAPIKey': GoogleMapsAPIKey}
		
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))


class EventCache(webapp.RequestHandler):
	def get(self):
		url = self.buildURL()
		
		try:
			response = fetch(url)
		except InvalidURLError as e:
			logging.error(e)
		
		eventsJSON = json.loads(response)
		
		events = self.createEventsFromJSON(eventsJSON)
		
		self.addEvents(events)
		
	def addEvents(self, events):
		pass
	
	def createEventsFromJSON(self, events):
		pass
		#greeting = Greeting()
		
		#greeting.content = self.request.get('content')
		#greeting.put()
	
	def buildURL(self, json=True):
		return None

application = webapp.WSGIApplication([('/', MainPage)],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()