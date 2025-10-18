import os
from flask import Flask, render_template, request, jsonify
import requests

# Initialize Flask app
app = Flask(__name__)

# --- CONFIGURATION ---
# IMPORTANT: Replace this with your actual OpenWeatherMap API key
# Get your key from: https://openweathermap.org/appid
api_key = os.environ.get('OPENWEATHER_API_KEY', "036f9a5cfd0f519bda32c3e462497fcd")
if api_key == "036f9a5cfd0f519bda32c3e462497fcd":
    print("Warning: API key is not set. Please get a key from OpenWeatherMap and set it in app.py")

# Base URL for the OpenWeatherMap API
API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


@app.route('/')
def index():
    """
    Renders the main page (index.html).
    """
    return render_template('index.html')


@app.route('/weather', methods=['POST'])
def get_weather():
    """
    Fetches weather data from OpenWeatherMap API based on city name from the frontend.
    Returns the data as JSON.
    """
    try:
        # Get city name from the JSON data sent by the frontend
        city = request.json.get('city')
        if not city:
            return jsonify({"error": "City name is required"}), 400

        # Construct the API request URL
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'  # Use 'imperial' for Fahrenheit
        }
        
        # Make the API call
        response = requests.get(API_BASE_URL, params=params)
        response.raise_for_status()  # This will raise an exception for HTTP errors (4xx or 5xx)

        data = response.json()

        # Check for API-specific errors (e.g., city not found)
        if data.get("cod") != 200:
            return jsonify({"error": data.get("message", "City not found")}), 404

        # Extract relevant weather information
        weather_info = {
            "city": data["name"],
            "temperature": f"{data['main']['temp']}°C",
            "description": data["weather"][0]["description"].capitalize(),
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} m/s",
            "icon": data["weather"][0]["icon"]
        }
        
        return jsonify(weather_info)

    except requests.exceptions.HTTPError as http_err:
        # Handle specific HTTP errors from the API
        if response.status_code == 404:
            return jsonify({"error": f"City '{city}' not found. Please check the spelling."}), 404
        elif response.status_code == 401:
             return jsonify({"error": "Invalid API key. Please check your key in app.py."}), 401
        else:
            return jsonify({"error": f"An API error occurred: {http_err}"}), response.status_code
            
    except requests.exceptions.RequestException as req_err:
        # Handle network-related errors (e.g., no internet connection)
        return jsonify({"error": f"Could not connect to weather service: {req_err}"}), 503

    except Exception as e:
        # Handle other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500


if __name__ == '__main__':
    # Runs the app in debug mode.
    # The host='0.0.0.0' makes the app accessible from other devices on the same network.
    app.run(host='0.0.0.0', port=5000, debug=True)
