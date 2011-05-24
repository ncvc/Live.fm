/**
 * Created on Apr 29, 2011
 * 
 * @author: Nathan V-C
 */

var SIMMONS_LATLONG = new google.maps.LatLng(42.357097, -71.101523);
var MY_LOC_IMAGE = 'images/blue_dot.png';
var EVENT_CACHE_URL = 'eventCache';
var map;
var locMethod;
var initialLocation;
var watchID;

function initialize() {
	createMap();
	getLocation();
}

function createMap() {
	var options = {
			zoom: 14,
			mapTypeId: google.maps.MapTypeId.ROADMAP
			};
		
	map = new google.maps.Map(document.getElementById('map_canvas'), options);
}

function setMyLocation(lat, long) {
	var myLatLng = new google.maps.LatLng(lat, long);
	
	var myLocMarker = new google.maps.Marker({
		position: myLatLng,
		map: map,
		icon: MY_LOC_IMAGE
		});
}

function getLocation() {
	if(navigator.geolocation) {
		// Try W3C Geolocation method (Preferred)
		locMethod = 'W3C standard';
		watchID = navigator.geolocation.watchPosition(function(position) {
			locationObtained(position.coords.latitude, position.coords.longitude);
		}, handleNoGeoLocation);
	} else if (google.gears) {
		// Try Google Gears Geolocation
		locMethod = 'Google Gears';
		var geo = google.gears.factory.create('beta.geolocation');
		geo.getCurrentPosition(function (position) {
			locationObtained(position.latitude, position.longitude);
		}, handleNoGeoLocation);
	} else {
		// Browser doesn't support Geolocation
		handleNoGeoLocation();
	}
}

function handleNoGeoLocation() {
	locMethod = 'Failed';
	locationObtained(SIMMONS_LATLONG.lat(), SIMMONS_LATLONG.long());
}

function locationObtained(lat, long) {
	centerMap(new google.maps.LatLng(lat, long));
	setMyLocation(lat, long);
	getEvents(lat, long);
}

function getEvents(lat, long) {
	var lookupURL = EVENT_CACHE_URL + '?lat=' + lat + '&long=' + long + '&dist=50';
	appendOut(lookupURL + '<br />');
	jQuery.getJSON(lookupURL, function(data) {
		//out.innerHTML += JSON.stringify(data);
		$.each(data.events.event, processEvents);
		appendOut(s);
		appendOut('<br />' + output);
	});
}
var s=0;
function processEvents(i, event) {
	s+=1;
	appendOut('<br />' + event.title + ': ' + JSON.stringify(event.venue.location));
	geoPoint = event.venue.location['geo:point'];
	createMarker(new google.maps.LatLng(geoPoint['geo:lat'], geoPoint['geo:long']), event.title);
}

function createMarker(latLong, title) {
	new google.maps.Marker({
		position: latLong,
		map: map,
		title: title
	});
}

function createInfoWindow(content, latLong) {
	new google.maps.InfoWindow({
		position: latLong,
		map: map,
		content: content
	});
}

function centerMap(initialLocation) {
	map.setCenter(initialLocation);
	
	appendOut(locMethod + '<br />');
}

function setOut(content) {
	out.innerHTML = content;
}

function appendOut(content) {
	out.innerHTML += content;
}