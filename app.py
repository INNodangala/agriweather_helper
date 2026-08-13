"""
AgriWeather Helper - Flask Application

A farming assistant app providing weather forecasts, crop advice,
planting schedules, and irrigation guidance for South African farmers.
"""

import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

from weather import (
    get_current_weather, get_forecast, get_weather_alerts,
    get_irrigation_recommendation, SA_CITIES
)
from crops import (
    get_all_crops, get_crop_info, get_seasonal_crops,
    get_crop_recommendations, get_planting_calendar, search_crops,
    get_current_month, get_water_needs_info
)
from irrigation import (
    calculate_water_need, get_irrigation_schedule, get_best_irrigation_time,
    calculate_irrigation_cost, get_drought_tips, get_soil_moisture_guidelines,
    compare_irrigation_methods, SOIL_TYPES, IRRIGATION_METHODS
)


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'agriweather-helper-dev-key')


@app.route('/')
def index():
    """Home page with weather overview."""
    return render_template('index.html', cities=SA_CITIES)


@app.route('/weather', methods=['POST'])
def weather():
    """Get weather for a city."""
    city = request.form.get('city', 'Cape Town')
    
    weather_data = get_current_weather(city)
    forecast_data = get_forecast(city)
    alerts = get_weather_alerts(weather_data)
    irrigation_rec = get_irrigation_recommendation(weather_data, forecast_data)
    
    return render_template('weather.html',
                          city=city,
                          weather=weather_data,
                          forecast=forecast_data,
                          alerts=alerts,
                          irrigation_rec=irrigation_rec,
                          cities=SA_CITIES)


@app.route('/api/weather/<city>')
def api_weather(city):
    """API endpoint for weather data."""
    weather_data = get_current_weather(city)
    return jsonify(weather_data)


@app.route('/api/forecast/<city>')
def api_forecast(city):
    """API endpoint for forecast data."""
    forecast_data = get_forecast(city)
    return jsonify(forecast_data)


@app.route('/crops')
def crops():
    """Crop information page."""
    all_crops = get_all_crops()
    seasonal = get_seasonal_crops()
    current_month = get_current_month()
    
    return render_template('crops.html',
                          crops=all_crops,
                          seasonal=seasonal,
                          current_month=current_month)


@app.route('/crops/<crop_name>')
def crop_detail(crop_name):
    """Crop detail page."""
    crop = get_crop_info(crop_name)
    if not crop:
        return render_template('404.html'), 404
    
    water_info = get_water_needs_info(crop['water_needs'])
    
    return render_template('crop_detail.html',
                          crop_name=crop_name,
                          crop=crop,
                          water_info=water_info)


@app.route('/planting')
def planting():
    """Planting calendar page."""
    calendar = get_planting_calendar()
    seasonal = get_seasonal_crops()
    
    return render_template('planting.html',
                          calendar=calendar,
                          seasonal=seasonal)


@app.route('/irrigation')
def irrigation():
    """Irrigation guide page."""
    methods = compare_irrigation_methods()
    soil_types = SOIL_TYPES
    drought_tips = get_drought_tips()
    
    return render_template('irrigation.html',
                          methods=methods,
                          soil_types=soil_types,
                          drought_tips=drought_tips)


@app.route('/irrigation/calculator', methods=['POST'])
def irrigation_calculator():
    """Irrigation calculator."""
    crop_name = request.form.get('crop', 'Maize')
    area = request.form.get('area', 1.0, type=float)
    soil_type = request.form.get('soil_type', 'loam')
    method = request.form.get('method', 'drip')
    
    water_need = calculate_water_need(crop_name, area)
    schedule = get_irrigation_schedule(crop_name, soil_type)
    cost = calculate_irrigation_cost(water_need['total_daily_liters'], method)
    soil_guide = get_soil_moisture_guidelines(soil_type)
    
    return render_template('irrigation_calculator.html',
                          water_need=water_need,
                          schedule=schedule,
                          cost=cost,
                          soil_guide=soil_guide,
                          crops=get_all_crops(),
                          soil_types=SOIL_TYPES,
                          methods=IRRIGATION_METHODS,
                          selected_crop=crop_name,
                          selected_area=area,
                          selected_soil=soil_type,
                          selected_method=method)


@app.route('/recommendations')
def recommendations():
    """Weather-based crop recommendations."""
    city = request.args.get('city', 'Cape Town')
    
    weather_data = get_current_weather(city)
    temperature = weather_data.get('temperature', 22)
    
    recommendations = get_crop_recommendations(temperature)
    
    return render_template('recommendations.html',
                          city=city,
                          weather=weather_data,
                          recommendations=recommendations)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
