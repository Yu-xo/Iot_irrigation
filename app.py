from flask import Flask, jsonify, render_template
import requests
from datetime import datetime
import time
from flask_cors import CORS
import logging
import random

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API keys
owm_api_key = "3353d596c7e7b60e7c9cf8f7b04bbe93"
waqi_api_key = "363fc83ab91e4680d693b24fcd39ce3cf585529c"

# Cache to store API responses and reduce API calls
cache = {
    'weather': {'data': None, 'timestamp': 0},
    'air_quality': {'data': None, 'timestamp': 0},
    'sensor_data': {
        'soil_moisture': 45.5,
        'soil_temperature': 22.3,
        'soil_ph': 6.8,
        'light_intensity': 850
    }
}
CACHE_DURATION = 300  # 5 minutes cache

def get_cached_data(cache_key, fetch_func, *args):
    current_time = time.time()
    if (cache[cache_key]['data'] is None or 
        current_time - cache[cache_key]['timestamp'] > CACHE_DURATION):
        try:
            cache[cache_key]['data'] = fetch_func(*args)
            cache[cache_key]['timestamp'] = current_time
        except Exception as e:
            logger.error(f"Error fetching {cache_key}: {str(e)}")
            if cache[cache_key]['data'] is None:
                raise
    return cache[cache_key]['data']

def get_location():
    try:
        response = requests.get("http://ipinfo.io/json", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching location: {str(e)}")
        return {'city': 'London'}  # Default fallback

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={owm_api_key}&units=metric"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather: {str(e)}")
        raise

def get_air_quality(city):
    try:
        url = f"http://api.waqi.info/feed/{city}/?token={waqi_api_key}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching air quality: {str(e)}")
        raise

def get_sensor_data():
    """
    Simulate sensor data with realistic variations
    """
    try:
        # Gradually change the sensor values to simulate real-world changes
        cache['sensor_data']['soil_moisture'] += random.uniform(-0.5, 0.5)
        cache['sensor_data']['soil_moisture'] = max(0, min(100, cache['sensor_data']['soil_moisture']))
        
        cache['sensor_data']['soil_temperature'] += random.uniform(-0.2, 0.2)
        cache['sensor_data']['soil_temperature'] = max(15, min(35, cache['sensor_data']['soil_temperature']))
        
        cache['sensor_data']['soil_ph'] += random.uniform(-0.1, 0.1)
        cache['sensor_data']['soil_ph'] = max(5.5, min(7.5, cache['sensor_data']['soil_ph']))
        
        cache['sensor_data']['light_intensity'] += random.uniform(-10, 10)
        cache['sensor_data']['light_intensity'] = max(0, min(2000, cache['sensor_data']['light_intensity']))
        
        return {
            'soil_moisture': round(cache['sensor_data']['soil_moisture'], 1),
            'soil_temperature': round(cache['sensor_data']['soil_temperature'], 1),
            'soil_ph': round(cache['sensor_data']['soil_ph'], 1),
            'light_intensity': round(cache['sensor_data']['light_intensity'], 0)
        }
    except Exception as e:
        logger.error(f"Error simulating sensor data: {str(e)}")
        raise

@app.route('/api/data')
def get_data():
    try:
        # Get location (not cached as it rarely changes during runtime)
        location_data = get_location()
        city = location_data.get('city', 'London')

        # Get weather data (cached)
        weather_data = get_cached_data('weather', get_weather, city)

        # Get air quality data (cached)
        air_quality_data = get_cached_data('air_quality', get_air_quality, city)

        # Get simulated sensor data
        sensor_data = get_sensor_data()

        # Combine all data
        combined_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'location': city,
            'weather': {
                'temperature': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'description': weather_data['weather'][0]['description']
            },
            'air_quality': air_quality_data['data']['aqi'] if 'data' in air_quality_data else 'N/A',
            'sensor_data': sensor_data
        }

        return jsonify(combined_data)

    except Exception as e:
        logger.error(f"Error in get_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
