"""
Crop module for AgriWeather Helper.

Provides crop information, recommendations, and planting schedules
for South African conditions.
"""


# Crop database with growing requirements
CROPS = {
    'Maize': {
        'category': 'Grain',
        'emoji': '🌽',
        'planting_season': 'Oct - Dec',
        'harvest_time': '4-6 months',
        'temp_range': (15, 35),
        'optimal_temp': 25,
        'water_needs': 'medium',
        'soil_type': 'Well-drained, fertile',
        'sunlight': 'Full sun',
        'description': 'South Africa\'s staple grain crop. Requires warm conditions and adequate rainfall.',
        'tips': [
            'Plant after last frost when soil is warm',
            'Needs regular water during tasseling',
            'Space plants 25-30cm apart',
            'Fertilize when plants are knee-high'
        ],
        'provinces': ['Mpumalanga', 'Free State', 'North West', 'Gauteng']
    },
    'Wheat': {
        'category': 'Grain',
        'emoji': '🌾',
        'planting_season': 'May - Jul',
        'harvest_time': '4-5 months',
        'temp_range': (10, 25),
        'optimal_temp': 18,
        'water_needs': 'medium',
        'soil_type': 'Well-drained clay-loam',
        'sunlight': 'Full sun',
        'description': 'Winter cereal crop important for bread production.',
        'tips': [
            'Plant in autumn for winter harvest',
            'Requires vernalization (cold period)',
            'Irrigate during dry spells',
            'Watch for rust disease'
        ],
        'provinces': ['Western Cape', 'Free State', 'Northern Cape']
    },
    'Potatoes': {
        'category': 'Vegetable',
        'emoji': '🥔',
        'planting_season': 'Aug - Mar',
        'harvest_time': '3-4 months',
        'temp_range': (15, 25),
        'optimal_temp': 20,
        'water_needs': 'high',
        'soil_type': 'Loose, well-drained',
        'sunlight': 'Full sun',
        'description': 'Important staple crop requiring consistent moisture.',
        'tips': [
            'Plant seed potatoes 10cm deep',
            'Hill soil around growing plants',
            'Keep soil consistently moist',
            'Harvest when foliage dies back'
        ],
        'provinces': ['Limpopo', 'Western Cape', 'Eastern Cape']
    },
    'Tomatoes': {
        'category': 'Vegetable',
        'emoji': '🍅',
        'planting_season': 'Aug - Jan',
        'harvest_time': '3-4 months',
        'temp_range': (18, 30),
        'optimal_temp': 24,
        'water_needs': 'medium',
        'soil_type': 'Rich, well-drained',
        'sunlight': 'Full sun',
        'description': 'Popular vegetable crop for fresh market and processing.',
        'tips': [
            'Start seeds indoors 6-8 weeks before planting',
            'Stake or cage plants for support',
            'Water at base to prevent disease',
            'Prune suckers for larger fruits'
        ],
        'provinces': ['All provinces']
    },
    'Sugarcane': {
        'category': 'Industrial',
        'emoji': '🎋',
        'planting_season': 'Aug - Feb',
        'harvest_time': '12-18 months',
        'temp_range': (20, 38),
        'optimal_temp': 30,
        'water_needs': 'high',
        'soil_type': 'Deep, fertile',
        'sunlight': 'Full sun',
        'description': 'Major industrial crop for sugar production in KZN.',
        'tips': [
            'Requires tropical/subtropical climate',
            'Needs abundant water',
            'Plant whole stalks horizontally',
            'First harvest after 12-18 months'
        ],
        'provinces': ['KwaZulu-Natal', 'Mpumalanga']
    },
    'Grapes': {
        'category': 'Fruit',
        'emoji': '🍇',
        'planting_season': 'Jul - Sep',
        'harvest_time': 'Feb - Apr',
        'temp_range': (15, 35),
        'optimal_temp': 25,
        'water_needs': 'low',
        'soil_type': 'Well-drained, rocky',
        'sunlight': 'Full sun',
        'description': 'Premium fruit for wine, table grapes, and juice.',
        'tips': [
            'Requires dry summers for quality',
            'Prune in winter for better yields',
            'Control water stress for wine grapes',
            'Train on trellis systems'
        ],
        'provinces': ['Western Cape', 'Northern Cape']
    },
    'Citrus': {
        'category': 'Fruit',
        'emoji': '🍊',
        'planting_season': 'Feb - Apr',
        'harvest_time': 'Jun - Sep',
        'temp_range': (15, 35),
        'optimal_temp': 25,
        'water_needs': 'medium',
        'soil_type': 'Well-drained, sandy-loam',
        'sunlight': 'Full sun',
        'description': 'Important export fruit including oranges, lemons, and grapefruit.',
        'tips': [
            'Protect from heavy frost',
            'Regular irrigation during dry season',
            'Prune to maintain tree shape',
            'Monitor for citrus psyllid'
        ],
        'provinces': ['Limpopo', 'Eastern Cape', 'KwaZulu-Natal']
    },
    'Soybeans': {
        'category': 'Legume',
        'emoji': '🫘',
        'planting_season': 'Oct - Dec',
        'harvest_time': '3-4 months',
        'temp_range': (18, 32),
        'optimal_temp': 26,
        'water_needs': 'medium',
        'soil_type': 'Well-drained, fertile',
        'sunlight': 'Full sun',
        'description': 'Important rotation crop and protein source.',
        'tips': [
            'Inoculate seeds with rhizobium',
            'Plant after last frost',
            'Good rotation crop with maize',
            'Harvest when pods are dry'
        ],
        'provinces': ['Mpumalanga', 'KwaZulu-Natal', 'Free State']
    },
    'Sunflowers': {
        'category': 'Oilseed',
        'emoji': '🌻',
        'planting_season': 'Nov - Jan',
        'harvest_time': '3-4 months',
        'temp_range': (18, 35),
        'optimal_temp': 25,
        'water_needs': 'low',
        'soil_type': 'Well-drained',
        'sunlight': 'Full sun',
        'description': 'Oilseed crop tolerant to drought conditions.',
        'tips': [
            'Drought tolerant once established',
            'Plant after soil温度 reaches 15°C',
            'Good rotation crop',
            'Harvest when back of heads turn brown'
        ],
        'provinces': ['Free State', 'North West', 'Mpumalanga']
    },
    'Avocados': {
        'category': 'Fruit',
        'emoji': '🥑',
        'planting_season': 'Feb - Apr',
        'harvest_time': '14-18 months',
        'temp_range': (15, 30),
        'optimal_temp': 22,
        'water_needs': 'medium',
        'soil_type': 'Deep, well-drained',
        'sunlight': 'Full sun to partial shade',
        'description': 'High-value export fruit requiring subtropical conditions.',
        'tips': [
            'Needs subtropical climate',
            'Protect from strong winds',
            'Regular irrigation essential',
            'Mulch to retain moisture'
        ],
        'provinces': ['Limpopo', 'Mpumalanga', 'KwaZulu-Natal']
    }
}


# Seasonal calendar for South Africa
SEASONAL_MONTHS = {
    'Spring': ['September', 'October', 'November'],
    'Summer': ['December', 'January', 'February'],
    'Autumn': ['March', 'April', 'May'],
    'Winter': ['June', 'July', 'August']
}


def get_all_crops():
    """Get list of all available crops."""
    return CROPS


def get_crop_info(crop_name):
    """Get detailed information about a specific crop."""
    return CROPS.get(crop_name)


def get_crops_by_season(season):
    """Get crops that can be planted in a specific season."""
    result = []
    for name, info in CROPS.items():
        if season.lower() in info['planting_season'].lower():
            result.append({'name': name, **info})
    return result


def get_current_planting_season():
    """Get current planting season based on date."""
    from datetime import datetime as _dt
    month = _dt.now().month
    
    if month in [9, 10, 11]:
        return 'Spring'
    elif month in [12, 1, 2]:
        return 'Summer'
    elif month in [3, 4, 5]:
        return 'Autumn'
    else:
        return 'Winter'


def get_seasonal_crops():
    """Get crops suitable for current season."""
    season = get_current_planting_season()
    return {
        'season': season,
        'crops': get_crops_by_season(season)
    }


def get_crop_recommendations(temperature, humidity=None):
    """
    Get crop recommendations based on weather conditions.
    
    Args:
        temperature (float): Current temperature in Celsius
        humidity (float): Current humidity percentage
    
    Returns:
        list: Recommended crops
    """
    recommendations = []
    
    for name, info in CROPS.items():
        temp_min, temp_max = info['temp_range']
        
        if temp_min <= temperature <= temp_max:
            # Calculate suitability score
            score = 100 - abs(temperature - info['optimal_temp']) * 2
            
            recommendations.append({
                'name': name,
                'emoji': info['emoji'],
                'category': info['category'],
                'suitability': max(0, min(100, score)),
                'planting_season': info['planting_season'],
                'water_needs': info['water_needs']
            })
    
    # Sort by suitability
    recommendations.sort(key=lambda x: x['suitability'], reverse=True)
    
    return recommendations[:6]


def get_water_needs_info(water_level):
    """Get information about water needs."""
    water_info = {
        'low': {
            'label': 'Low',
            'description': 'Drought tolerant, minimal irrigation needed',
            'frequency': '1-2 times per week',
            'icon': 'tint'
        },
        'medium': {
            'label': 'Medium',
            'description': 'Regular watering, keep soil moist',
            'frequency': '3-4 times per week',
            'icon': 'tint'
        },
        'high': {
            'label': 'High',
            'description': 'Needs consistent moisture, frequent watering',
            'frequency': 'Daily or every other day',
            'icon': 'tint'
        }
    }
    return water_info.get(water_level, water_info['medium'])


def get_current_month():
    """Get current month name."""
    from datetime import datetime
    return datetime.now().strftime('%B')


def get_planting_calendar():
    """Get planting calendar for all crops."""
    calendar = {}
    
    for name, info in CROPS.items():
        season = info['planting_season']
        if season not in calendar:
            calendar[season] = []
        calendar[season].append({
            'name': name,
            'emoji': info['emoji'],
            'harvest': info['harvest_time']
        })
    
    return calendar


def search_crops(query):
    """Search crops by name or category."""
    results = []
    query = query.lower()
    
    for name, info in CROPS.items():
        if query in name.lower() or query in info['category'].lower():
            results.append({'name': name, **info})
    
    return results
