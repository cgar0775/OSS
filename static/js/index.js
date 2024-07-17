let map;
let service;
let infowindow;

function initialize_Map() {
    fetch('/get-user-location')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching user location:', data.error);
                return;
            }
            const userLocation = new google.maps.LatLng(data.lat, data.lng);
            map = new google.maps.Map(document.getElementById('map'), {
                center: userLocation,
                zoom: 13
            });

            infowindow = new google.maps.InfoWindow(); // Initialize infowindow

            const userMarker = new google.maps.Marker({
                position: userLocation,
                map: map,
                icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                title: 'Your Location'
            });

            // Add click event listener to userMarker (Use for Business)
            userMarker.addListener('click', function() {
                infowindow.setContent('You Are Here');
                infowindow.open(map, userMarker);
            });

            const request = {
                location: userLocation,
                radius: '32186',  // 20 miles in meters
                type: ['store']   // Search for stores; you can change the type as needed
            };

            service = new google.maps.places.PlacesService(map);
            service.nearbySearch(request, callback);
        })
        .catch(error => console.error('Error fetching user location:', error));
}

function callback(results, status) {
    if (status === google.maps.places.PlacesServiceStatus.OK) {
        for (let i = 0; i < results.length; i++) {
            createMarker(results[i]);
        }
    }
}

function createMarker(place) {
    const placeLoc = place.geometry.location;
    const marker = new google.maps.Marker({
        map: map,
        position: placeLoc,
        icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
    });

    google.maps.event.addListener(marker, 'click', function() {
        infowindow.setContent(`<div><strong>${place.name}</strong><br>
                               Address: ${place.vicinity}<br>
                               <img src="${place.photos ? place.photos[0].getUrl() : ''}" alt="Image" style="width:100px;height:100px;"><br>
                               Location: ${placeLoc}</div>`);
        infowindow.open(map, marker);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initialize_Map();
});
