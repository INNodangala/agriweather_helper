"""
Weather module for AgriWeather Helper.

Handles weather data fetching and processing.
Uses OpenWeatherMap API for weather data.
"""

import os
import requests
from datetime import datetime, timedelta


# Default API key - users should set their own
DEFAULT_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
BASE_URL = 'https://api.openweathermap.org/data/2.5'


def get_current_weather(city, api_key=None, units='metric'):
    """
    Get current weather for a city.
    
    Args:
        city (str): City name
        api_key (str): OpenWeatherMap API key
        units (str): 'metric' or 'imperial'
    
    Returns:
        dict: Weather data or error
    """
    if not api_key:
        api_key = DEFAULT_API_KEY
    
    if not api_key:
        return _get_mock_weather(city)
    
    try:
        url = f'{BASE_URL}/weather'
        params = {
            'q': city,
            'appid': api_key,
            'units': units
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'success': True,
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'].title(),
            'icon': data['weather'][0]['icon'],
            'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # Convert m/s to km/h
            'pressure': data['main']['pressure'],
            'visibility': round(data.get('visibility', 0) / 1000, 1),
            'clouds': data['clouds']['all'],
            'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
    except requests.RequestException as e:
        return {'success': False, 'error': str(e)}


def get_forecast(city, days=5, api_key=None, units='metric'):
    """
    Get weather forecast for a city.
    
    Args:
        city (str): City name
        days (int): Number of days (max 5)
        api_key (str): OpenWeatherMap API key
        units (str): 'metric' or 'imperial'
    
    Returns:
        dict: Forecast data or error
    """
    if not api_key:
        api_key = DEFAULT_API_KEY
    
    if not api_key:
        return _get_mock_forecast(city, days)
    
    try:
        url = f'{BASE_URL}/forecast'
        params = {
            'q': city,
            'appid': api_key,
            'units': units,
            'cnt': days * 8  # 8 forecasts per day (every 3 hours)
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Process forecast into daily summaries
        daily_forecasts = []
        current_date = None
        daily_data = []
        
        for item in data['list']:
            forecast_date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            
            if forecast_date != current_date:
                if daily_data:
                    daily_forecasts.append(_summarize_daily(current_date, daily_data))
                current_date = forecast_date
                daily_data = []
            
            daily_data.append(item)
        
        if daily_data:
            daily_forecasts.append(_summarize_daily(current_date, daily_data))
        
        return {
            'success': True,
            'city': data['city']['name'],
            'country': data['city']['country'],
            'forecasts': daily_forecasts[:days]
        }
    except requests.RequestException as e:
        return {'success': False, 'error': str(e)}


def _summarize_daily(date_str, forecasts):
    """Summarize multiple forecasts into daily data."""
    temps = [f['main']['temp'] for f in forecasts]
    humidity = [f['main']['humidity'] for f in forecasts]
    rain_chance = [f.get('pop', 0) * 100 for f in forecasts]
    
    # Get most common weather condition
    conditions = [f['weather'][0]['description'] for f in forecasts]
    main_condition = max(set(conditions), key=conditions.count)
    icon = forecasts[0]['weather'][0]['icon']
    
    return {
        'date': date_str,
        'day_name': datetime.strptime(date_str, '%Y-%m-%d').strftime('%A'),
        'temp_min': round(min(temps)),
        'temp_max': round(max(temps)),
        'temp_avg': round(sum(temps) / len(temps)),
        'humidity_avg': round(sum(humidity) / len(humidity)),
        'rain_chance': round(max(rain_chance)),
        'description': main_condition.title(),
        'icon': icon
    }


def _get_mock_weather(city):
    """Return mock weather data when API key is not available."""
    return {
        'success': True,
        'city': city.title(),
        'country': 'ZA',
        'temperature': 24,
        'feels_like': 25,
        'humidity': 65,
        'description': 'Partly Cloudy',
        'icon': '02d',
        'wind_speed': 12.5,
        'pressure': 1013,
        'visibility': 10.0,
        'clouds': 40,
        'sunrise': '06:30',
        'sunset': '18:45',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'mock': True
    }


def _get_mock_forecast(city, days):
    """Return mock forecast data when API key is not available."""
    forecasts = []
    base_date = datetime.now()
    
    conditions = [
        ('Partly Cloudy', '02d'),
        ('Sunny', '01d'),
        ('Light Rain', '10d'),
        ('Cloudy', '04d'),
        ('Clear', '01d')
    ]
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        cond = conditions[i % len(conditions)]
        
        forecasts.append({
            'date': date.strftime('%Y-%m-%d'),
            'day_name': date.strftime('%A'),
            'temp_min': 18 + (i % 3),
            'temp_max': 26 + (i % 4),
            'temp_avg': 22 + (i % 3),
            'humidity_avg': 55 + (i * 5),
            'rain_chance': (i * 15) % 100,
            'description': cond[0],
            'icon': cond[1]
        })
    
    return {
        'success': True,
        'city': city.title(),
        'country': 'ZA',
        'forecasts': forecasts,
        'mock': True
    }


def get_weather_alerts(weather_data):
    """
    Generate farming alerts based on weather conditions.
    
    Args:
        weather_data (dict): Current weather data
    
    Returns:
        list: List of alerts
    """
    alerts = []
    
    if not weather_data.get('success'):
        return alerts
    
    temp = weather_data.get('temperature', 20)
    humidity = weather_data.get('humidity', 50)
    wind = weather_data.get('wind_speed', 0)
    description = weather_data.get('description', '').lower()
    
    # Temperature alerts
    if temp > 35:
        alerts.append({
            'type': 'danger',
            'icon': 'thermometer',
            'title': 'Extreme Heat Warning',
            'message': 'Temperature above 35°C. Ensure adequate irrigation and consider shade for sensitive crops.'
        })
    elif temp > 30:
        alerts.append({
            'type': 'warning',
            'icon': 'thermometer',
            'title': 'High Temperature',
            'message': 'Warm conditions. Monitor soil moisture and increase irrigation if needed.'
        })
    elif temp < 5:
        alerts.append({
            'type': 'danger',
            'icon': 'snowflake',
            'title': 'Frost Warning',
            'message': 'Temperature near freezing. Protect sensitive crops from frost damage.'
        })
    elif temp < 10:
        alerts.append({
            'type': 'warning',
            'icon': 'temperature-low',
            'title': 'Cold Conditions',
            'message': 'Cool temperatures may slow crop growth. Consider cold-sensitive planting.'
        })
    
    # Rain alerts
    if 'rain' in description or 'storm' in description:
        alerts.append({
            'type': 'info',
            'icon': 'cloud-rain',
            'title': 'Rain Expected',
            'message': 'Rain conditions. Postpone spraying and check drainage systems.'
        })
    
    # Wind alerts
    if wind > 40:
        alerts.append({
            'type': 'warning',
            'icon': 'wind',
            'title': 'Strong Winds',
            'message': 'High wind speeds may damage crops. Secure loose structures and young plants.'
        })
    
    # Humidity alerts
    if humidity > 85:
        alerts.append({
            'type': 'warning',
            'icon': 'droplet',
            'title': 'High Humidity',
            'message': 'High humidity increases disease risk. Monitor for fungal infections.'
        })
    elif humidity < 30:
        alerts.append({
            'type': 'info',
            'icon': 'droplet',
            'title': 'Low Humidity',
            'message': 'Dry conditions. Increase irrigation frequency for shallow-rooted crops.'
        })
    
    return alerts


def get_irrigation_recommendation(weather_data, forecast_data=None):
    """
    Get irrigation recommendation based on weather.
    
    Args:
        weather_data (dict): Current weather
        forecast_data (dict): Forecast data
    
    Returns:
        dict: Irrigation recommendation
    """
    if not weather_data.get('success'):
        return {'recommendation': 'Data unavailable', 'urgency': 'unknown'}
    
    temp = weather_data.get('temperature', 20)
    humidity = weather_data.get('humidity', 50)
    rain_chance = 0
    
    if forecast_data and forecast_data.get('success'):
        forecasts = forecast_data.get('forecasts', [])
        if forecasts:
            rain_chance = forecasts[0].get('rain_chance', 0)
    
    # Calculate irrigation need
    if rain_chance > 70:
        return {
            'recommendation': 'Skip irrigation - rain expected',
            'urgency': 'low',
            'icon': 'cloud-rain',
            'details': 'Significant rain chance. Natural watering should suffice.'
        }
    elif rain_chance > 40:
        return {
            'recommendation': 'Light irrigation recommended',
            'urgency': 'medium',
            'icon': 'tint',
            'details': 'Some rain possible, but light irrigation may be needed.'
        }
    elif temp > 30 and humidity < 40:
        return {
            'recommendation': 'Increase irrigation frequency',
            'urgency': 'high',
            'icon': 'exclamation-triangle',
            'details': 'Hot and dry conditions. Crops need more water than usual.'
        }
    elif temp > 25 and humidity < 60:
        return {
            'recommendation': 'Regular irrigation schedule',
            'urgency': 'medium',
            'icon': 'tint',
            'details': 'Moderate conditions. Follow your regular irrigation plan.'
        }
    else:
        return {
            'recommendation': 'Reduce irrigation',
            'urgency': 'low',
            'icon': 'check-circle',
            'details': 'Cool and humid conditions. Less water needed.'
        }


# South African cities for quick selection
SA_CITIES = [
    'Cape Town', 'Johannesburg', 'Durban', 'Pretoria', 'Port Elizabeth',
    'Bloemfontein', 'East London', 'Nelspruit', 'Polokwane', 'Kimberley',
    'Pietermaritzburg', 'Rustenburg', 'Soweto', 'Vereeniging', 'Stellenbosch',
    'George', 'Upington', 'Richards Bay', 'Klerksdorp', 'Benoni'
]
