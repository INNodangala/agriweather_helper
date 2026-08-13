# AgriWeather Helper

A farming assistant app providing weather forecasts, crop advice, planting schedules, and irrigation guidance for South African farmers.

## Features

- **Weather Forecasts**: Current weather and 5-day forecasts for SA cities
- **Crop Guide**: Information on major South African crops
- **Planting Calendar**: Know what to plant and when
- **Irrigation Guide**: Smart water management and scheduling
- **Crop Recommendations**: Weather-based crop suggestions
- **Irrigation Calculator**: Calculate water needs and costs

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Navigate to the AgriWeatherHelper directory:
   ```bash
   cd AgriWeatherHelper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Set your OpenWeatherMap API key:
   ```bash
   export OPENWEATHER_API_KEY=your_api_key_here
   ```
   Get a free API key at https://openweathermap.org/api

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and go to:
   ```
   http://localhost:5001
   ```

## Features

### Weather
- Current temperature, humidity, wind speed
- 5-day forecast
- Farming alerts based on conditions
- Irrigation recommendations

### Crops
- Growing conditions and requirements
- Planting seasons for SA
- Water needs information
- Province-specific growing info

### Irrigation
- Water need calculations
- Irrigation scheduling
- Cost estimates
- Soil moisture guidelines
- Drought conservation tips

## Project Structure

```
AgriWeatherHelper/
├── app.py              # Flask application
├── weather.py          # Weather API integration
├── crops.py            # Crop database
├── irrigation.py       # Irrigation calculations
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
├── static/             # CSS, JS
└── data/               # Data files
```

## Disclaimer

Weather data is for guidance only. Always check local conditions before making farming decisions.
