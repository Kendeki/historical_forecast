import requests as r
import pandas as pd
from datetime import date, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import root_mean_squared_error, precision_score

def models(lat:float = 0, lon:float = 0):

    def group_weather(code):
        if code == 0:
            return 0
        elif code in [1,2,3]:
            return 1  
        elif code in [45,48]:
            return 2  
        elif code in [51,53,55,56,57]:
            return 3  
        elif code in [61,63,65,66,67,80,81,82]:
            return 4  
        elif code in [71,73,75,77,85,86]:
            return 5  
        elif code in [95,96,99]:
            return 6
    
    weather_code = {
        0: "Clear Sky",
        1: "Cloudy",
        2: "Fog",
        3: "Drizzle",
        4: "Rain",
        5: "Snow",
        6: "Thunderstorm"
    }

    data = pd.DataFrame(response['daily'], index=response["daily"]["time"])
    data = pd.concat(data, pd.DataFrame(response['daily'], index=['daily']['time']))
    
    data = data.drop(columns=["time"])
    data["weather_code"] = data["weather_code"].apply(group_weather)
    length = len(data)

    for column in data:
        if column == "weather_code":
            continue
        data[column+'1'] = data[column].shift(1)
        data[column+'2'] = data[column].shift(2)
    data = data.fillna(0)

    size_train = int(data.shape[0]*0.8)

    # /----- Temperature Prediction -----/

    temperatures = ["temperature_2m_max", "apparent_temperature_max", "apparent_temperature_min", 
                    "temperature_2m_mean", "temperature_2m_min", "apparent_temperature_mean"]
    
    modelTemp = LinearRegression()

    x_train = data.iloc[:size_train, :].drop(columns=temperatures)
    x_test  = data.iloc[size_train:, :].drop(columns=temperatures)
    y_train = data[temperatures].iloc[:size_train]
    y_test  = data[temperatures].iloc[size_train:]

    modelTemp.fit(x_train, y_train)
    predT = modelTemp.predict(x_test)
    rmce = [root_mean_squared_error(predT[:, i], y_test.iloc[:, i]) 
            for i in range(len(temperatures))]
    # /----- Weather Prediction -----/

    counts = data["weather_code"].value_counts()
    weights = {weight: counts.sum()/count for weight, count in counts.items()}
    modelWeather = RandomForestClassifier(class_weight=weights, random_state=67)

    x_train = data.iloc[:size_train, length:]
    x_test  = data.iloc[size_train:, length:]
    y_train = data.iloc[:size_train, 0]
    y_test  = data.iloc[size_train:, 0]

    modelWeather.fit(x_train, y_train)
    predW = modelWeather.predict(x_test)
    prc = precision_score(predW, y_test)

    return {"temperatures": predT[-1], 
            "margin": rmce, 
            "weather": weather_code[predW[-1]], 
            "precision": prc}

def main():
    results = models()
    print(results)
    
if __name__ == '__main__':
    main()