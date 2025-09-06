import requests as r
import json as j
from datetime import date, timedelta
from time import sleep
from random import uniform

coords = [(round(uniform(-90, 90), 6), 
                round(uniform(-180, 180), 6)) for _ in range(50)]

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 0,
    "longitude": 0,
    "start_date":"",
    "end_date": "",
    "timezone": "America/Sao_Paulo",
    "daily": ["weather_code", "dew_point_2m_mean", "pressure_msl_mean", "surface_pressure_mean",
            "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum",
            "daylight_duration", "sunshine_duration", "precipitation_hours",
            "precipitation_sum", "snowfall_sum", "showers_sum", "rain_sum", "temperature_2m_mean",
            "apparent_temperature_mean", "cloud_cover_mean"]
}

def create_json(start_date="2023-01-01", end_date="2024-01-01"):
    params["start_date"] = start_date
    params["end_date"] = end_date

    for lat, lon in coords:
        sleep(10)
        params["latitude"] = lat
        params["longitude"] = lon
        
        try:
            response = r.get(url=url, params=params).json()
        except (j.decoder.JSONDecodeError, r.exceptions.RequestException):
            continue
        if response.get("error", False):
            print(f"Erro de gravação com as coordenadas ({lat}, {lon}).")
            print(response['reason'])
            continue

        print(f"Gravação concluída com as coordenadas ({lat}, {lon}).")
        with open("data.ndjson", 'a') as f:
            f.write(j.dumps(response) + '\n')

def user_test_data(lat: float, lon: float):
    params["latitude"] = lat
    params["longitude"] = lon
    params["start_date"] = str(date.today() - timedelta(days=365))
    params["end_date"] = str(date.today() - timedelta(days=2))

    try:
        response = r.get(url=url, params=params).json()
    except (j.decoder.JSONDecodeError, r.exceptions.RequestException):
        raise RuntimeError(f'Erro ao acessar a API. Tente novamente.')
    
    if response.get("error", False):
        raise RuntimeError(f"Erro ao acessar as coordenadas ({lat}, {lon}).\n{response['reason']}")

    print(f"Dados para teste às coordenadas ({lat}, {lon}) foram obtidas.")
    return response

def tomorrows_prediction_data(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params["latitude"] = lat
    params["longitude"] = lon
    params["start_date"] = str(date.today())
    params["end_date"] = str(date.today())

    try:
        response = r.get(url=url, params=params).json()
    except (j.decoder.JSONDecodeError, r.exceptions.RequestException):
        raise RuntimeError(f'Erro ao acessar a API. Tente novamente.')
    
    if response.get("error", False):
        raise RuntimeError(f"Erro ao acessar as coordenadas ({lat}, {lon}).\n{response['reason']}")

    print(f"Acesso concluído às coordenadas ({lat}, {lon})")
    return response
    
if __name__ == '__main__':
    create_json()
    create_json(start_date="2024-01-02", end_date="2025-01-01")
