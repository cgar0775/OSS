let map;
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

            // Add marker for user's location
            const userMarker = new google.maps.Marker({
                position: userLocation,
                map: map,
                icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                title: 'Your Location'
            });

            // Add click event listener to userMarker
            userMarker.addListener('click', function() {
                infowindow.setContent('You Are Here');
                infowindow.open(map, userMarker);
            });

            // Fetch and display nearby businesses
            fetch('/get_nearby_businesses')
                .then(response => response.json())
                .then(businesses => {
                    businesses.forEach(business => {
                        const businessLocation = new google.maps.LatLng(business[2], business[3]); // assuming business[2] is lat and business[3] is lng
                        const businessMarker = new google.maps.Marker({
                            position: businessLocation,
                            map: map,
                            icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                            title: business[1] // assuming business[1] is the business name
                        });

                        businessMarker.addListener('click', function() {
                            infowindow.setContent(`<div><strong>${business[0]}</strong><br>
                                                   Location: ${businessLocation}</div>`);
                            infowindow.open(map, businessMarker);
                        });
                    });
                })
                .catch(error => console.error('Error fetching nearby businesses:', error));
        })
        .catch(error => console.error('Error fetching user location:', error));
}

function createMarker(business) {
    const placeLoc = new google.maps.LatLng(business[1], business[2]); // Adjust according to your data structure
    const marker = new google.maps.Marker({
        map: map,
        position: placeLoc,
        icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
    });

    marker.addListener('click', function() {
        infowindow.setContent(`<div><strong>${business[1]}</strong><br>
                               Address: ${business[2]}, ${business[3]}</div>`);
        infowindow.open(map, marker);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initialize_Map();
});
