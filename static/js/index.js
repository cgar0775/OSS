let map;
let service;
let infowindow;

function initialize_Map() {
    const center = new google.maps.LatLng(29.6520, -82.3250);  // Default center (Gainesville)
    map = new google.maps.Map(document.getElementById('map'), {
        center: center,
        zoom: 13
    });
    infowindow = new google.maps.InfoWindow();
}

function searchBusinesses() {
    const searchInput = document.getElementById('searchInput').value;
    const geocoder = new google.maps.Geocoder();
    
    geocoder.geocode({ 'address': searchInput }, function(results, status) {
        if (status == 'OK') {
            map.setCenter(results[0].geometry.location);
            const request = {
                location: results[0].geometry.location,
                radius: '32186',  // 20 miles in meters
                type: ['business']   // Search for stores; you can change the type as needed
            };
            service = new google.maps.places.PlacesService(map);
            service.nearbySearch(request, callback);
        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}

function callback(results, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
        for (let i = 0; i < results.length; i++) {
            createMarker(results[i]);
        }
    }
}

function createMarker(place) {
    const placeLoc = place.geometry.location;
    const marker = new google.maps.Marker({
        map: map,
        position: placeLoc
    });

    google.maps.event.addListener(marker, 'click', function() {
        infowindow.setContent(`<div><strong>${place.name}</strong><br>
                               Address: ${place.vicinity}<br>
                               <img src="${place.photos ? place.photos[0].getUrl() : ''}" alt="Image" style="width:100px;height:100px;"><br>
                               Location: ${placeLoc}</div>`);
        infowindow.open(map, this);
    });
}
