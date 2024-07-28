function performSearch(searchTerm) {
    getUserLocation(function(location) {
        const searchUrl = `/search?search=${encodeURIComponent(searchTerm)}&location=${encodeURIComponent(location)}`;
        window.location.href = searchUrl;
    });
}

function initCategorySearch() {
    const iconBoxes = document.querySelectorAll('.icon-box');
    iconBoxes.forEach(box => {
        box.addEventListener('click', function() {
            const searchTerm = this.getAttribute('data-search-term');
            performSearch(searchTerm);
        });
    });
}

function getUserLocation(callback) {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            fetch(`https://api.opencagedata.com/geocode/v1/json?q=${latitude}+${longitude}&key=ba66aa30e94d4cd8b1154d7752ffba6d`)
                .then(response => response.json())
                .then(data => {
                    const city = data.results[0].components.city;
                    const state = data.results[0].components.state;
                    callback(`${city}, ${state}`);
                })
                .catch(error => {
                    console.error('Error:', error);
                    callback("New York, NY");  // Default fallback
                });
        }, function(error) {
            console.error("Error: " + error.message);
            callback("New York, NY");  // Default fallback
        });
    } else {
        console.log("Geolocation is not supported by this browser.");
        callback("New York, NY");  // Default fallback
    }
}

document.addEventListener('DOMContentLoaded', initCategorySearch);