'''
Created on Apr 17, 2011

@author: Nathan V-C
'''

import cgi
import os
import logging

import urllib

from datetime import datetime
from django.utils import simplejson as json

from APIKeys import GMAPS_API_KEY
from APIKeys import LASTFM_API_KEY

from google.appengine.api import taskqueue
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api.urlfetch import fetch, InvalidURLError

DEFAULT_LINK = None
DEFAULT_IMAGE_LINK = 'http://www.google.com/images/logos/ps_logo2.png'
DEFAULT_PHONE_NUMBER = None

LASTFM_API_BASE_URL = 'http://ws.audioscrobbler.com/2.0/'
DEFAULT_LAT = '42.357097'
DEFAULT_LONG = '-71.101523'
DEFAULT_DIST = '10' #km
DEFAULT_LIMIT = '10'

DEBUG = True
	
class Event(db.Model):
	eventID = db.IntegerProperty()
	eventTitle = db.StringProperty()
	eventDescription = db.TextProperty()
	eventImageURLs = db.ListProperty(db.Link)
	eventAttendance = db.IntegerProperty()
	eventReviews = db.IntegerProperty()
	eventTag = db.StringProperty()
	eventURL = db.LinkProperty()
	eventWebsite = db.LinkProperty()
	eventTickets = db.TextProperty()
	eventCancelled = db.BooleanProperty()
	
	venueID = db.IntegerProperty()
	venueName = db.StringProperty()
	venueURL = db.LinkProperty()
	venueWebsite = db.LinkProperty()
	venuePhoneNumber = db.PhoneNumberProperty()
	venueImageURLs = db.ListProperty(db.Link)
	venueAddress = db.PostalAddressProperty()
	venueTimeZone = db.StringProperty()
	
	artists = db.StringListProperty()
	headliner = db.StringProperty()
	
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
		
		template_values = {'GoogleMapsAPIKey': GMAPS_API_KEY,
						   'Size': '100%'}
		
		if DEBUG:
			template_values.update({'Size': '50%',
									'debug': '<p id="out">out: </p>'})
		
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))

class EventCache(webapp.RequestHandler):
	def get(self):
		lat = self.request.get('lat', default_value=DEFAULT_LAT)
		long = self.request.get('long', default_value=DEFAULT_LONG)
		dist = self.request.get('dist', default_value=DEFAULT_DIST)
		# get closest points
		self.response.out.write(lastFMResponse.content)

class UpdateCache(webapp.RequestHandler):
	def get(self):
		url = self.buildURL()
		
		try:
			lastFMResponse = fetch(url)
			self.response.out.write(lastFMResponse.content)
			return
		except InvalidURLError as e:
			logging.error(e)
			return
		
		if self.JSONError(lastFMResponse.content):
			return
		
		eventsJSON = json.loads(lastFMResponse.content)
		
		events = self.createEventsFromJSON(eventsJSON)
		
		self.addEvents(events)
		
	
	# build the url to retrieve event info from the Last.fm API
	def buildURL(self, json=True):
		limit = self.request.get('limit', default_value=DEFAULT_LIMIT)
		page = 1
		
		query = {'method': 'geo.getevents',
				'limit': limit,
				'page': page,
				'api_key': LASTFM_API_KEY}
		
		if json:
			query['format'] = 'json'
		
		encoded = urllib.urlencode(query)
		
		return '%s?%s' % (LASTFM_API_BASE_URL, encoded)
	
	# Returns a list of Event objects resulting from parsing the given JSON
	def createEventsFromJSON(self, eventsFullJSON):
		eventsList = []
		eventsJSON = eventsFullJSON['events']['event']
		
		for eventJSON in eventsJSON:
			event = Event()
			event.eventID = int(eventJSON['id'])
			event.eventTitle = eventJSON['title']
			
			artistsJSON = eventJSON['artists']
			event.artists = self.createStrList(artistsJSON['artist'])
			event.headliner = artistsJSON['headliner']
			
			venueJSON = eventJSON['venue']
			event.venueID = int(venueJSON['id'])
			event.venueName = venueJSON['name']
			
			locJSON = venueJSON['location']
			geoJSON = locJSON['geo:point']
			address, geoPt = self.parseAddress(locJSON['street'], locJSON['city'], locJSON['country'], locJSON['postalcode'])
			if geoPt == None:
				geoPt = db.GeoPt(geoJSON['geo:lat'], geoJSON['geo:long'])
			event.geoPt = geoPt
			event.venueAddress = db.PostalAddress(address)
			
			event.venueURL = self.createLink(venueJSON['url'])
			event.venueWebsite = self.createLink(venueJSON['website'])
			event.venuePhoneNumber = self.createPhoneNumber(venueJSON['phonenumber'])
			event.venueImageURLs = self.getImageURLs(venueJSON['image'])
			
			# Sample date string: "Mon, 02 May 2011 22:00:00"
			formatStr = '%a, %d %b %Y %H:%M:%S'
			event.date = datetime.strptime(eventJSON['startDate'], formatStr)
			event.eventDescription = eventJSON['description']
			event.eventImageURLs = self.getImageURLs(eventJSON['image'])
			event.eventAttendance = int(eventJSON['attendance'])
			event.eventReviews = int(eventJSON['reviews'])
			event.eventTag = eventJSON['tag']
			event.eventURL = self.createLink(eventJSON['url'])
			event.eventWebsite = self.createLink(eventJSON['website'])
			event.eventTickets = str(eventJSON['tickets'])
			event.eventCancelled = bool(int(eventJSON['cancelled']))
			
			try:
				event.tags = self.createStrList(eventJSON['tags']['tag'])
			except KeyError:
				pass
			
			eventsList.append(event)
		
		return eventsList
	
	# Parses address info and returns an address string and a db.GeoPt
	def parseAddress(self, street, city, country, postalcode):
		
		line1 = street
		line2 = '%s, %s %s' % (city, country, postalcode)
		address = '%s\n%s' % (line1, line2)
		return address, db.GeoPt()
	
	# returns a list of string(s) from the given JSON object
	def createStrList(self, JSONStr):
		if isinstance(JSONStr, unicode) or isinstance(JSONStr, str):
			return [JSONStr]
		else:
			return JSONStr
	
	# Returns a new db.Link from the given URL
	def createLink(self, url, default=DEFAULT_LINK):
		if url == None or url == '':
			return default
		else:
			return db.Link(url)
	
	# Returns a new db.PhoneNumber from the given phone number
	def createPhoneNumber(self, number, default=DEFAULT_PHONE_NUMBER):
		if number == None or number == '':
			return default
		else:
			return db.PhoneNumber(number)
	
	# Returns a list of image URLs from the given JSON
	def getImageURLs(self, imagesJSON):
		imageURLs = []
		for imageJSON in imagesJSON:
			link = self.createLink(imageJSON['#text'], default=DEFAULT_IMAGE_LINK)
			imageURLs.append(link)
		
		return imageURLs
	
	# Adds all events to the database
	def addEvents(self, events):
		for event in events:
			event.put()
	
	# Returns whether or not an error was returned in the given JSON
	def JSONError(self, responseJSON):
		if 'error' in responseJSON:
			logging.error(responseJSON)
			return True
		else:
			return False

application = webapp.WSGIApplication([('/', MainPage),
									  ('/eventCache', EventCache),
									  ('/updateCache', UpdateCache)],
									 debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()