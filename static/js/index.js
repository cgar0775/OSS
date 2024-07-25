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
                        const businessLocation = new google.maps.LatLng(business[2], business[3]);
                        const businessMarker = new google.maps.Marker({
                            position: businessLocation,
                            map: map,
                            icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                            title: business[1]
                        });

                        businessMarker.addListener('click', function() {
                            infowindow.setContent(`<div><strong>${business[1]}</strong><br>
                                                   Location: ${business[2]}, ${business[3]}</div>`);
                            infowindow.open(map, businessMarker);
                        });
                    });
                })
                .catch(error => console.error('Error fetching nearby businesses:', error));
        })
        .catch(error => console.error('Error fetching user location:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    initialize_Map();
});
