function updateDashboard() {
    fetch('http://localhost:5000/api/data')
        .then(response => response.json())
        .then(data => {
            // Update weather information
            document.getElementById('location').textContent = data.location;
            document.getElementById('temperature').textContent = `${data.weather.temperature}°C`;
            document.getElementById('humidity').textContent = `${data.weather.humidity}%`;
            document.getElementById('weather-desc').textContent = data.weather.description;

            // Update air quality
            document.getElementById('aqi').textContent = data.air_quality;

            // Update soil conditions
            document.getElementById('soil-moisture').textContent = data.sensor_data.soil_moisture.toFixed(1);
            document.getElementById('soil-temperature').textContent = data.sensor_data.soil_temperature.toFixed(1);
            document.getElementById('soil-ph').textContent = data.sensor_data.soil_ph.toFixed(1);

            // Update light conditions
            document.getElementById('light-intensity').textContent = data.sensor_data.light_intensity.toFixed(0);

            // Update timestamp
            document.getElementById('timestamp').textContent = data.timestamp;
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Update dashboard immediately and then every 5 seconds
updateDashboard();
setInterval(updateDashboard, 5000);
