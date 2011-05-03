/**
 * 
 */

var SIMMONS = new google.maps.LatLng(42.357097, -71.101523);
var map;
var infowindow = new google.maps.InfoWindow();

function initialize() {
	createMap();
	
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
			
			showMap(new google.maps.LatLng(position.coords.latitude, position.coords.longitude));
		}, handleNoGeoLocation);
	} else if (google.gears) {
		// Try Google Gears Geolocation
		contentString = "Location found using Google Gears";
		initialLocation = new google.maps.LatLng(position.latitude, position.longitude);
		var geo = google.gears.factory.create('beta.geolocation');
		geo.getCurrentPosition(function (position) {
			showMap(new google.maps.LatLng(position.latitude, position.longitude));
		}, handleNoGeoLocation);
	} else {
		// Browser doesn't support Geolocation
		handleNoGeoLocation();
	}
}

function handleNoGeoLocation() {
	contentString = "Error: The Geolocation service failed. Defaulting to Simmons. Represent!";
	showMap(SIMMONS);
}

function showMap(initialLocation) {
	map.setCenter(initialLocation);
	parseXML();
	infowindow.setContent(contentString);
	infowindow.setPosition(initialLocation);
	infowindow.open(map);
}

function parseXML() {
	if (window.XMLHttpRequest) {
		xmlhttp = new XMLHttpRequest();
	} else {
		xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
	}
	xmlhttp.open("GET", "http://ws.audioscrobbler.com/2.0/?method=geo.getevents&location=madrid&api_key=b25b959554ed76058ac220b7b2e0a026", false);
	xmlhttp.send();
	contentString = xmlhttp.responseXML;
}