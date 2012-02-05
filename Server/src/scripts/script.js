/**
 * Created on Apr 29, 2011
 * 
 * @author: Nathan V-C
 */

var DEFAULT_LATLONG = new google.maps.LatLng(42.357097, -71.101523);
var MY_LOC_IMAGE = 'images/blue_dot.png';
var EVENT_CACHE_URL = 'eventCache';
var DEFAULT_ZOOM = 14;
var DEFAULT_MAP_TYPE = google.maps.MapTypeId.ROADMAP;
var MAP_CANVAS_ID = 'map_canvas';
var map;
var watchID;

function initialize() {
	createMap();
	getLocation();
}

/*
 * Displays a Google Map object on the page
 */
function createMap() {
	var options = {
			zoom: DEFAULT_ZOOM,
			mapTypeId: DEFAULT_MAP_TYPE
			};
		
	map = new google.maps.Map(document.getElementById(MAP_CANVAS_ID), options);
}

/*
 * Sets the user's location and and places a marker there
 */
function setMyLocation(lat, long) {
	var myLatLng = new google.maps.LatLng(lat, long);
	
	var myLocMarker = new google.maps.Marker({
		position: myLatLng,
		map: map,
		icon: MY_LOC_IMAGE
		});
}

/*
 * Gets the user's current location and calls locationObtained when a position is found
 */
function getLocation() {
	if(navigator.geolocation) {
		// Try W3C Geolocation method (Preferred)
		watchID = navigator.geolocation.watchPosition(function(position) {
			locationObtained(position.coords.latitude, position.coords.longitude, 'W3C standard');
		}, handleNoGeoLocation);
	} else if (google.gears) {
		// Try Google Gears Geolocation
		var geo = google.gears.factory.create('beta.geolocation');
		geo.getCurrentPosition(function (position) {
			locationObtained(position.latitude, position.longitude, 'Google Gears');
		}, handleNoGeoLocation);
	} else {
		// Browser doesn't support Geolocation
		handleNoGeoLocation();
	}
}

/*
 * Calls locationObtained with a default location and locMethod='Failed'
 */
function handleNoGeoLocation() {
	locationObtained(DEFAULT_LATLONG.lat(), DEFAULT_LATLONG.long(), 'Failed');
}

/*
 * Centers the map on the given location and displays events close to said location
 */
function locationObtained(lat, long, locMethod) {
	appendOut('locationMethod:' + locMethod + '<br />');
	
	map.setCenter(new google.maps.LatLng(lat, long));
	setMyLocation(lat, long);
	findEvents(lat, long);
}

/*
 * Gets events near the given location and displays them on the map
 */
function findEvents(lat, long) {
	var lookupURL = EVENT_CACHE_URL + '?lat=' + lat + '&long=' + long + '&dist=50';
	appendOut(lookupURL + '<br />');
	jQuery.getJSON(lookupURL, function(data) {
		appendOut(JSON.stringify(data));
		$.each(data.events.event, processEvent);
		appendOut(s);
		appendOut('<br />' + output);
	});
}

var s=0;
/*
 * Displays the given event on the map
 */
function processEvent(i, event) {
	s+=1;
	appendOut('<br />' + event.title + ': ' + JSON.stringify(event.venue.location));
	geoPoint = event.venue.location['geo:point'];
	createMarker(new google.maps.LatLng(geoPoint['geo:lat'], geoPoint['geo:long']), event.title);
}

/*
 * Displays a marker on the map with the given location and title
 */
function createMarker(latLong, title) {
	new google.maps.Marker({
		position: latLong,
		map: map,
		title: title
	});
}

/*
 * Displays an InfoWindow on the map with the given location and title
 */
function createInfoWindow(content, latLong) {
	new google.maps.InfoWindow({
		position: latLong,
		map: map,
		content: content
	});
}

/*
 * Sets debug output
 */
function setOut(content) {
	out.innerHTML = content;
}

/*
 * Appends to debug output
 */
function appendOut(content) {
	out.innerHTML += content;
}