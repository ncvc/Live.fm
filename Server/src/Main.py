'''
Created on Apr 20, 2011

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
	eventTickets = db.IntegerProperty()
	eventCancelled = db.IntegerProperty()
	
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
			response = fetch(url)
		except InvalidURLError as e:
			logging.error(e)
			return
		
		eventsJSON = json.loads(response)
		
		events = self.createEventsFromJSON(eventsJSON)
		
		self.addEvents(events)
	
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
		
		encoded = urllib.urlencode(query)
		
		return '%s?%s' % (baseURL, encoded)
	
	def createEventsFromJSON(self, eventsFullJSON):
		eventsList = []
		eventsJSON = eventsFullJSON['events']['event']
		
		for eventJSON in eventsJSON:
			event = Event()
			event.eventID = eventJSON['id']
			event.eventTitle = eventJSON['title']
			
			artistsJSON = eventJSON['artists']
			event.artists = artistsJSON['artist']
			event.headliner = artistsJSON['headliner']
			
			venueJSON = eventJSON['venue']
			event.venueID = venueJSON['id']
			event.venueName = venueJSON['name']
			
			locJSON = venueJSON['location']
			geoJSON = locJSON['geo:point']
			event.geoPt = db.GeoPt(geoJSON['geo:lat'], geoJSON['geo:long'])
			line1 = locJSON['street']
			line2 = '%s, %s %s' % (locJSON['city'], locJSON['country'], locJSON['postalcode'])
			address = '%s\n%s' % (line1, line2)
			event.venueAddress = db.PostalAddress(address)
			
			event.venueURL = db.Link(venueJSON['url'])
			event.venueWebsite = db.Link(venueJSON['website'])
			event.venuePhoneNumber = db.PhoneNumber(venueJSON['phonenumber'])
			event.venueImageURLs = self.getImageURLs(venueJSON['image'])
			
			# Sample string: "Mon, 02 May 2011 22:00:00"
			formatStr = '%a, %d %b %Y %H:%M:%S'
			event.date = datetime.strptime(eventJSON['startdate'], formatStr)
			event.eventDescription = eventJSON['description']
			event.eventImageURLs = self.getImageURLs(eventJSON['image'])
			event.eventAttendance = eventJSON['attendance']
			event.eventReviews = eventJSON['reviews']
			event.eventTag = eventJSON['tag']
			event.eventURL = db.Link(eventJSON['url'])
			event.eventWebsite = db.Link(eventJSON['website'])
			event.eventTickets = eventJSON['tickets']
			event.eventCancelled = eventJSON['cancelled']
			
			eventsList.append(event)
		
		return eventsList
	
	def getImageURLs(self, imagesJSON):
		imageURLs = []
		for imageJSON in imagesJSON:
			imageURLs.append(db.Link(imageJSON['#text']))
		
		return imageURLs
		
	def addEvents(self, events):
		for event in events:
			event.put()

application = webapp.WSGIApplication([('/', MainPage)],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()