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

from APIKeys import GoogleMapsAPIKey
from APIKeys import LastFMAPIKey

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api.urlfetch import fetch, InvalidURLError

DEFAULT_LINK = 'http://www.google.com'
DEFAULT_IMAGE_LINK = 'http://www.google.com/images/logos/ps_logo2.png'
DEFAULT_PHONE_NUMBER = '1234567890'
	
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
		
		template_values = {'GoogleMapsAPIKey': GoogleMapsAPIKey}
		
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))


class EventCache(webapp.RequestHandler):
	def get(self):
		url = self.buildURL()
		
		try:
			lastFMResponse = fetch(url)
		except InvalidURLError as e:
			logging.error(e)
			return
		
		if self.JSONError(lastFMResponse.content):
			return
		
		eventsJSON = json.loads(lastFMResponse.content)
		
		events = self.createEventsFromJSON(eventsJSON)
		
		self.addEvents(events)
		
		self.response.out.write(lastFMResponse.content)
	
	def buildURL(self, json=True):
		baseURL = 'http://ws.audioscrobbler.com/2.0/'
		defaultLat = '42.357097'
		defaultLong = '-71.101523'
		
		lat = self.request.get('lat', default_value=None)
		long = self.request.get('long', default_value=None)
		dist = 10 #km
		limit = 10
		page = 1
		
		if lat == None:
			lat = defaultLat
		if long == None:
			long = defaultLong
		
		query = {'method': 'geo.getevents',
				'lat': lat,
				'long': long,
				'distance': dist,
				'limit': limit,
				'page': page,
				'api_key': LastFMAPIKey}
		
		if json:
			query['format'] = 'json'
		
		encoded = urllib.urlencode(query)
		
		return '%s?%s' % (baseURL, encoded)
	
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
			event.geoPt = db.GeoPt(geoJSON['geo:lat'], geoJSON['geo:long'])
			line1 = locJSON['street']
			line2 = '%s, %s %s' % (locJSON['city'], locJSON['country'], locJSON['postalcode'])
			address = '%s\n%s' % (line1, line2)
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
	
	def createStrList(self, JSONStr):
		if isinstance(JSONStr, unicode) or isinstance(JSONStr, str):
			return [JSONStr]
		else:
			return JSONStr
	
	def createLink(self, url, default=DEFAULT_LINK):
		if url == None or url == '':
			return db.Link(default)
		else:
			return db.Link(url)
	
	def createPhoneNumber(self, number, default=DEFAULT_PHONE_NUMBER):
		if number == None or number == '':
			return db.PhoneNumber(default)
		else:
			return db.PhoneNumber(number)
	
	def getImageURLs(self, imagesJSON):
		imageURLs = []
		for imageJSON in imagesJSON:
			link = self.createLink(imageJSON['#text'], default=DEFAULT_IMAGE_LINK)
			imageURLs.append(link)
		
		return imageURLs
		
	def addEvents(self, events):
		for event in events:
			event.put()
	
	def JSONError(self, responseJSON):
		if 'error' in responseJSON:
			logging.error(responseJSON)
			return True
		else:
			return False

application = webapp.WSGIApplication([('/', MainPage),
									  ('/eventCache', EventCache)],
									 debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()