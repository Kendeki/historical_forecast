import requests as r
import json as j
from datetime import date, timedelta
from random import uniform
coords = [(round(uniform(-90, 90), 6), 
                round(uniform(-180, 180), 6)) for _ in range(30)]

params = {
    "latitude": 0,
    "longitude": 0,
    "start_date": date.today() - timedelta(days=1),
    "end_date": str(date.today() - timedelta(days=730)),
    "timezone": "America/Sao_Paulo",
    "daily": ["weather_code", "cape_mean", "dew_point_2m_mean", 
            "pressure_msl_mean", "surface_pressure_mean", "temperature_2m_max", 
            "apparent_temperature_max", "apparent_temperature_min", "wind_speed_10m_max", 
            "wind_gusts_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum", 
            "daylight_duration", "sunshine_duration", "uv_index_max", "uv_index_clear_sky_max", 
            "precipitation_hours", "precipitation_probability_max", "precipitation_sum", 
            "snowfall_sum", "showers_sum", "rain_sum", "cape_min", "cape_max", 
            "temperature_2m_mean", "temperature_2m_min", "apparent_temperature_mean", 
            "dew_point_2m_max", "dew_point_2m_min", "cloud_cover_min", "cloud_cover_max", 
            "cloud_cover_mean"],
}

def create_json():
    for (lat, lon) in coords:
        params["latitude"] = lat
        params["longitude"] = lon
        url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
        response = r.get(url=url, params=params).json()

        try:
            if response['error']:
                continue
        except KeyError:
            with open("data.ndjson", 'a') as f:
                f.write(j.dumps(response) + '\n')



def checkToday():
        url = "https://api.open-meteo.com/v1/forecast"
        params["start_date"] = str(date.today())
        params["end_date"] = params["start_date"]

        with open("data.ndjson", 'a') as f:
            f.write(j.dumps(response) + '\n')


create_json()