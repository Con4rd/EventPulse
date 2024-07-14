// Function to get the user's geolocation
function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(sendLocationToServer, handleLocationError);
    } else {
        console.error("Geolocation is not supported by this browser.");
    }
}

function sendLocationToServer(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    fetch('/location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ latitude, longitude }),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // Handle the response from the server if needed
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function handleLocationError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            console.error("User denied the request for geolocation.");
            // Display a message to the user indicating that location access was denied
            break;
        case error.POSITION_UNAVAILABLE:
            console.error("Location information is unavailable.");
            // Display a message to the user indicating that location information is unavailable
            break;
        case error.TIMEOUT:
            console.error("The request to get user location timed out.");
            // Display a message to the user indicating that the location request timed out
            break;
        case error.UNKNOWN_ERROR:
            console.error("An unknown error occurred.");
            // Display a generic error message to the user
            break;
    }
}

// Call the function to get the user's location when the page loads
window.onload = getUserLocation;