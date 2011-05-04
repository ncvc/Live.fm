/**
 * Created on Apr 29, 2011
 * 
 * @author: Nathan V-C
 */

var SIMMONS_LATLONG = new google.maps.LatLng(42.357097, -71.101523);
var EVENT_CACHE_URL = "eventCache";
var map;

function initialize() {
	createMap();
	''
	getLocation();
}

function createMap() {
	var myOptions = {
			zoom: 14,
			mapTypeId: google.maps.MapTypeId.ROADMAP
			};
		
	map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
}

function getLocation() {
	// Try W3C Geolocation method (Preferred)
	if(navigator.geolocation) {
		contentString = "Location found using W3C standard";
		navigator.geolocation.getCurrentPosition(function (position) {
			locationObtained(position.coords.latitude, position.coords.longitude);
		}, handleNoGeoLocation);
	} else if (google.gears) {
		// Try Google Gears Geolocation
		contentString = "Location found using Google Gears";
		initialLocation = new google.maps.LatLng(position.latitude, position.longitude);
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
	contentString = "Error: The Geolocation service failed. Defaulting to Simmons. Represent!";
	locationObtained(SIMMONS_LATLONG.lat(), SIMMONS_LATLONG.long());
}

function locationObtained(lat, long) {
	centerMap(new google.maps.LatLng(lat, long));
	getEvents(lat, long)
}

function getEvents(lat, long) {
	var lookupURL = EVENT_CACHE_URL + "?lat=" + lat + "&long=" + long;
	setOut(lookupURL);
	jQuery.getJSON(lookupURL, function(data) {
		//out.innerHTML += JSON.stringify(data);
		$.each(data.events.event, processEvents);
		appendOut(s);
		appendOut("<br />" + output);
	})
}
var s=0;
function processEvents(i, event) {
	s+=1;
	appendOut("<br />" + event.title + ": " + JSON.stringify(event.venue.location));
	geoPoint = event.venue.location["geo:point"];
	createMarker(new google.maps.LatLng(geoPoint["geo:lat"], geoPoint["geo:long"]), event.title);
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
	
	createInfoWindow(contentString, initialLocation)
}

function setOut(content) {
	out.innerHTML = content;
}

function appendOut(content) {
	out.innerHTML += content;
}