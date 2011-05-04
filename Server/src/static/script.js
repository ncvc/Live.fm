/**
 * Created on Apr 29, 2011
 * 
 * @author: Nathan V-C
 */

var SIMMONS = new google.maps.LatLng(42.357097, -71.101523);
var map;
var infowindow = new google.maps.InfoWindow();

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
	locationObtained(SIMMONS.lat(), SIMMONS.long());
}

function locationObtained(lat, long) {
	showMap(new google.maps.LatLng(lat, long));
	getEvents(lat, long)
}

function getEvents(lat, long) {
	jQuery.getJSON("eventCache", function(data) {
		//out.innerHTML += JSON.stringify(data);
		$.each(data.events.event, processEvents);
		out.innerHTML += s;
		out.innerHTML += "<br />" + output;
	})
}
var s=0;
var output = "";
function processEvents(i, event) {
	s+=1;
	output += "<br />" + event.title + ": " + JSON.stringify(event.venue.location);
	geoPoint = event.venue.location["geo:point"];
	createMarker(new google.maps.LatLng(geoPoint["geo:lat"], geoPoint["geo:long"]), event.title);
}

function createMarker(latLng, title) {
	var marker = new google.maps.Marker({
		position: latLng,
		map: map,
		title: title
	});
}

function showMap(initialLocation) {
	map.setCenter(initialLocation);
	
	infowindow.setContent(contentString);
	infowindow.setPosition(initialLocation);
	infowindow.open(map);
}