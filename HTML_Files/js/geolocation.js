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
    console.error('Error Code = ' + error.code + ' - ' + error.message);
}

// Call the function to get the user's location when the page loads
window.onload = getUserLocation;
