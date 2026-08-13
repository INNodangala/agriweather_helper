"""
Irrigation module for AgriWeather Helper.

Provides irrigation scheduling, calculations, and recommendations
based on weather conditions and crop needs.
"""

from datetime import datetime, timedelta


# Evapotranspiration rates by month (mm/day) for South Africa
ET_RATES = {
    1: 6.5,   # January (Summer)
    2: 6.0,   # February
    3: 5.0,   # March (Autumn)
    4: 3.5,   # April
    5: 2.5,   # May
    6: 1.5,   # June (Winter)
    7: 1.5,   # July
    8: 2.5,   # August
    9: 3.5,   # September (Spring)
    10: 5.0,  # October
    11: 6.0,  # November
    12: 6.5   # December (Summer)
}

# Crop coefficients (Kc) for different growth stages
CROP_COEFFICIENTS = {
    'Maize': {'initial': 0.3, 'mid': 1.2, 'late': 0.6},
    'Wheat': {'initial': 0.3, 'mid': 1.15, 'late': 0.25},
    'Potatoes': {'initial': 0.5, 'mid': 1.15, 'late': 0.75},
    'Tomatoes': {'initial': 0.6, 'mid': 1.15, 'late': 0.8},
    'Sugarcane': {'initial': 0.4, 'mid': 1.25, 'late': 0.75},
    'Grapes': {'initial': 0.3, 'mid': 0.85, 'late': 0.45},
    'Citrus': {'initial': 0.65, 'mid': 0.65, 'late': 0.65},
    'Soybeans': {'initial': 0.4, 'mid': 1.15, 'late': 0.5},
    'Sunflowers': {'initial': 0.35, 'mid': 1.15, 'late': 0.35},
    'Avocados': {'initial': 0.6, 'mid': 0.85, 'late': 0.6}
}

# Soil types and their water-holding capacity
SOIL_TYPES = {
    'sandy': {
        'name': 'Sandy',
        'capacity': 'Low',
        'drainage': 'Fast',
        'irrigation_freq': 'Frequent',
        'water_holding': 75  # mm per meter depth
    },
    'loam': {
        'name': 'Loam',
        'capacity': 'Medium',
        'drainage': 'Moderate',
        'irrigation_freq': 'Regular',
        'water_holding': 150
    },
    'clay': {
        'name': 'Clay',
        'capacity': 'High',
        'drainage': 'Slow',
        'irrigation_freq': 'Less frequent',
        'water_holding': 225
    },
    'silt': {
        'name': 'Silt',
        'capacity': 'Medium-High',
        'drainage': 'Moderate',
        'irrigation_freq': 'Regular',
        'water_holding': 175
    }
}

# Irrigation methods
IRRIGATION_METHODS = {
    'drip': {
        'name': 'Drip Irrigation',
        'efficiency': 90,
        'description': 'Water delivered directly to plant roots through emitters',
        'pros': ['Water efficient', 'Reduces weeds', 'Lower disease risk'],
        'cons': ['Higher setup cost', 'Requires filtration', 'Can clog'],
        'best_for': ['Vegetables', 'Fruit trees', 'Row crops']
    },
    'sprinkler': {
        'name': 'Sprinkler Irrigation',
        'efficiency': 75,
        'description': 'Water sprayed through the air like rainfall',
        'pros': ['Good coverage', 'Versatile', 'Moderate cost'],
        'cons': ['Wind affected', 'Higher evaporation', 'Foliage wetting'],
        'best_for': ['Lawns', 'Grains', 'Pastures']
    },
    'flood': {
        'name': 'Flood/Furrow Irrigation',
        'efficiency': 50,
        'description': 'Water flows across the field through furrows',
        'pros': ['Low cost', 'Simple', 'No special equipment'],
        'cons': ['Water wasteful', 'Uneven distribution', 'Erosion risk'],
        'best_for': ['Rice', 'Large grain fields']
    },
    'center_pivot': {
        'name': 'Center Pivot',
        'efficiency': 80,
        'description': 'Large rotating sprinkler system for circular fields',
        'pros': ['Large coverage', 'Consistent', 'Automated'],
        'cons': ['Very expensive', 'Fixed circle shape', 'High energy'],
        'best_for': ['Large farms', 'Grains', 'Row crops']
    }
}


def calculate_water_need(crop_name, area_hectares, growth_stage='mid'):
    """
    Calculate water need for a crop.
    
    Args:
        crop_name (str): Name of the crop
        area_hectares (float): Area in hectares
        growth_stage (str): 'initial', 'mid', or 'late'
    
    Returns:
        dict: Water need calculation
    """
    month = datetime.now().month
    et_rate = ET_RATES.get(month, 4.0)
    
    # Get crop coefficient
    kc_data = CROP_COEFFICIENTS.get(crop_name, {'initial': 0.5, 'mid': 1.0, 'late': 0.5})
    kc = kc_data.get(growth_stage, 1.0)
    
    # Calculate daily water need (mm/day)
    daily_water_mm = et_rate * kc
    
    # Convert to liters per hectare (1mm = 10,000 L/ha)
    daily_liters_ha = daily_water_mm * 10000
    
    # Total for area
    total_daily_liters = daily_liters_ha * area_hectares
    total_weekly_liters = total_daily_liters * 7
    
    return {
        'crop': crop_name,
        'area_hectares': area_hectares,
        'growth_stage': growth_stage,
        'et_rate': et_rate,
        'crop_coefficient': kc,
        'daily_mm': round(daily_water_mm, 1),
        'daily_liters_per_ha': round(daily_liters_ha),
        'total_daily_liters': round(total_daily_liters),
        'total_weekly_liters': round(total_weekly_liters),
        'month': datetime.now().strftime('%B')
    }


def get_irrigation_schedule(crop_name, soil_type='loam', weather_condition='normal'):
    """
    Get irrigation schedule recommendation.
    
    Args:
        crop_name (str): Crop name
        soil_type (str): Soil type
        weather_condition (str): 'dry', 'normal', 'wet'
    
    Returns:
        dict: Irrigation schedule
    """
    soil = SOIL_TYPES.get(soil_type, SOIL_TYPES['loam'])
    crop_kc = CROP_COEFFICIENTS.get(crop_name, {'mid': 1.0})
    kc = crop_kc.get('mid', 1.0)
    
    # Base interval (days) adjusted for soil and weather
    base_interval = 3
    
    # Adjust for soil type
    if soil_type == 'sandy':
        base_interval = 2
    elif soil_type == 'clay':
        base_interval = 4
    
    # Adjust for weather
    if weather_condition == 'dry':
        base_interval = max(1, base_interval - 1)
    elif weather_condition == 'wet':
        base_interval = min(7, base_interval + 2)
    
    # Calculate irrigation amount (mm)
    amount_mm = 20 * kc  # Typical irrigation depth
    
    return {
        'crop': crop_name,
        'soil_type': soil['name'],
        'weather': weather_condition,
        'interval_days': base_interval,
        'amount_mm': round(amount_mm),
        'amount_liters_per_ha': round(amount_mm * 10000),
        'best_time': 'Early morning (06:00 - 09:00)',
        'tips': [
            f'Irrigate every {base_interval} days',
            f'Apply {amount_mm}mm per irrigation',
            f'Best time: Early morning',
            'Check soil moisture before irrigation',
            'Avoid irrigation during hot midday'
        ]
    }


def get_best_irrigation_time(weather_data):
    """Get best irrigation time based on weather."""
    temp = weather_data.get('temperature', 25)
    humidity = weather_data.get('humidity', 50)
    
    if temp > 30:
        return {
            'best_time': 'Early Morning (05:00 - 08:00)',
            'reason': 'Avoid high evaporation during hot day',
            'avoid': 'Midday (11:00 - 15:00)'
        }
    elif humidity > 80:
        return {
            'best_time': 'Late Afternoon (16:00 - 18:00)',
            'reason': 'High humidity reduces evaporation loss',
            'avoid': 'Early morning when humidity is highest'
        }
    else:
        return {
            'best_time': 'Early Morning (06:00 - 09:00)',
            'reason': 'Optimal conditions for water absorption',
            'avoid': 'Late evening (can promote disease)'
        }


def calculate_irrigation_cost(liters, method='drip'):
    """
    Calculate estimated irrigation cost.
    
    Args:
        liters (float): Water volume in liters
        method (str): Irrigation method
    
    Returns:
        dict: Cost estimate
    """
    # Water cost (municipal - rough estimate)
    water_cost_per_1000 = 25  # R25 per 1000 liters (rough estimate)
    
    # Efficiency factor
    efficiency = IRRIGATION_METHODS.get(method, {}).get('efficiency', 75) / 100
    
    # Actual water needed (accounting for efficiency)
    actual_water = liters / efficiency
    
    # Calculate cost
    water_cost = (actual_water / 1000) * water_cost_per_1000
    
    # Energy cost (rough estimate for pumping)
    energy_cost = actual_water * 0.002  # R0.002 per liter for pumping
    
    return {
        'liters_requested': round(liters),
        'actual_water_needed': round(actual_water),
        'efficiency': f'{int(efficiency * 100)}%',
        'water_cost': round(water_cost, 2),
        'energy_cost': round(energy_cost, 2),
        'total_cost': round(water_cost + energy_cost, 2),
        'currency': 'ZAR'
    }


def get_drought_tips():
    """Get water conservation tips for drought conditions."""
    return [
        'Irrigate early morning to reduce evaporation',
        'Use mulch to retain soil moisture',
        'Water deeply but less frequently',
        'Prioritize crops by value and water needs',
        'Collect rainwater when possible',
        'Use drip irrigation for efficiency',
        'Avoid watering during windy conditions',
        'Check for leaks in irrigation systems',
        'Use soil moisture sensors',
        'Consider drought-tolerant crop varieties'
    ]


def get_soil_moisture_guidelines(soil_type):
    """Get soil moisture management guidelines."""
    soil = SOIL_TYPES.get(soil_type, SOIL_TYPES['loam'])
    
    return {
        'soil_type': soil['name'],
        'water_holding': soil['capacity'],
        'drainage': soil['drainage'],
        'irrigation_frequency': soil['irrigation_freq'],
        'guidelines': [
            f'{soil["name"]} soil has {soil["capacity"].lower()} water-holding capacity',
            f'Drainage is {soil["drainage"].lower()}',
            f'Irrigation frequency: {soil["irrigation_freq"]}',
            'Check soil moisture 10-15cm below surface',
            'Soil should feel moist but not waterlogged'
        ]
    }


def get_irrigation_method_info(method):
    """Get information about irrigation method."""
    return IRRIGATION_METHODS.get(method)


def compare_irrigation_methods():
    """Compare different irrigation methods."""
    comparisons = []
    
    for key, method in IRRIGATION_METHODS.items():
        comparisons.append({
            'key': key,
            'name': method['name'],
            'efficiency': method['efficiency'],
            'description': method['description'],
            'best_for': method['best_for']
        })
    
    # Sort by efficiency
    comparisons.sort(key=lambda x: x['efficiency'], reverse=True)
    
    return comparisons
