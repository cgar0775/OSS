let map;
let infowindow;

function getDistance(lat1, lng1, lat2, lng2) {
    const R = 3958.8; // Radius of Earth in miles
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

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

            infowindow = new google.maps.InfoWindow();

            const userMarker = new google.maps.Marker({
                position: userLocation,
                map: map,
                icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                title: 'Your Location'
            });

            userMarker.addListener('click', function() {
                infowindow.setContent('You Are Here');
                infowindow.open(map, userMarker);
            });

            fetch('/get-nearby-businesses')
                .then(response => response.json())
                .then(businesses => {
                    businesses.forEach(business => {
                        const businessLocation = new google.maps.LatLng(business.lat, business.lng);
                        const distance = getDistance(data.lat, data.lng, business.lat, business.lng);

                        if (distance <= 20) { // 20 miles
                            const businessMarker = new google.maps.Marker({
                                position: businessLocation,
                                map: map,
                                icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                                title: business.name
                            });

                            businessMarker.addListener('click', function() {
                                infowindow.setContent(`<div><strong>${business.name}</strong><br>
                                                       Address: ${business.address}</div>`);
                                infowindow.open(map, businessMarker);
                            });
                        }
                    });
                })
                .catch(error => console.error('Error fetching nearby businesses:', error));
        })
        .catch(error => console.error('Error fetching user location:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    initialize_Map();
});
