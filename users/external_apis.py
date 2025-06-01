import requests
from django.conf import settings
from typing import Dict, Optional

class WeatherAPI:
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    @staticmethod
    def get_weather(city: str) -> Optional[Dict]:
        """
        Get current weather for a city using OpenWeatherMap API.
        Returns None if the API call fails.
        """
        try:
            params = {
                'q': city,
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric'  # Use metric units
            }
            response = requests.get(WeatherAPI.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            return None

def attach_weather_to_note(note_data: Dict, city: str) -> Dict:
    """
    Attaches weather information to note data if a city is provided.
    """
    if city:
        weather_data = WeatherAPI.get_weather(city)
        if weather_data:
            note_data['weather'] = {
                'temperature': weather_data['main']['temp'],
                'description': weather_data['weather'][0]['description'],
                'humidity': weather_data['main']['humidity'],
                'city': city
            }
    return note_data 