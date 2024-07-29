function performSearch(searchTerm) {
    getUserLocation(function(location) {
        console.log(`Retrieved location: ${location}`);
        if (location) {
            const searchUrl = `/search?search=${encodeURIComponent(searchTerm)}&location=${encodeURIComponent(location)}`;
            console.log(`Redirecting to: ${searchUrl}`);
            window.location.href = searchUrl;
        } else {
            console.log("Location not available");
            // Prompt user to enter their location
            let userLocation = prompt("We couldn't determine your location. Please enter your city and state (e.g., New York, NY):");
            if (userLocation) {
                const searchUrl = `/search?search=${encodeURIComponent(searchTerm)}&location=${encodeURIComponent(userLocation)}`;
                console.log(`Redirecting to: ${searchUrl}`);
                window.location.href = searchUrl;
            } else {
                alert("A location is required to search for events. Please try again.");
            }
        }
    });
}


function initCategorySearch() {
    const iconBoxes = document.querySelectorAll('.icon-box');
    iconBoxes.forEach(box => {
        box.addEventListener('click', function() {
            const searchTerm = this.querySelector('.title').textContent;
            console.log(`Category clicked: ${searchTerm}`);
            performSearch(searchTerm);
        });
    });
}

function getUserLocation(callback) {
    // First, try to get location from browser's geolocation API
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                console.log(`Geolocation successful: Lat ${latitude}, Long ${longitude}`);
                reverseGeocode(latitude, longitude, callback);
            },
            function(error) {
                console.error("Geolocation error:", error);
                useIPFallback(callback);
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    } else {
        console.log("Geolocation is not supported by this browser.");
        useIPFallback(callback);
    }
}

function reverseGeocode(latitude, longitude, callback) {
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`)
        .then(response => response.json())
        .then(data => {
            console.log("Reverse geocoding response:", data);
            const city = data.address.city || data.address.town || data.address.village;
            const state = data.address.state;
            if (city && state) {
                const location = `${city}, ${state}`;
                console.log(`Resolved location: ${location}`);
                callback(location);
            } else {
                console.log("Couldn't resolve location from reverse geocoding");
                useIPFallback(callback);
            }
        })
        .catch(error => {
            console.error('Reverse geocoding Error:', error);
            useIPFallback(callback);
        });
}

function useIPFallback(callback) {
    fetch('https://ipapi.co/json/')
        .then(response => response.json())
        .then(data => {
            console.log("IP Geolocation API response:", data);
            const city = data.city;
            const state = data.region;
            if (city && state) {
                const location = `${city}, ${state}`;
                console.log(`Resolved location (IP fallback): ${location}`);
                callback(location);
            } else {
                console.error("Couldn't resolve location from IP");
                callback(null);
            }
        })
        .catch(error => {
            console.error('IP Geolocation API Error:', error);
            callback(null);
        });
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    initCategorySearch();
});