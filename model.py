import pandas as pd
from dataFormer import tomorrows_prediction_data, user_test_data
from json import loads
from math import ceil
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import root_mean_squared_error, precision_score

def models(latitude: float, longitude: float):
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

    data_list = []
    prediction_list = []

    with open("data.ndjson", "r", encoding="utf-8") as f:
        for line in f:
            record    = loads(line)
            lat       = record["latitude"]
            lon       = record["longitude"]
            daily     = record["daily"]
            data_temp = pd.DataFrame(daily)

            data_temp["latitude"]  = lat
            data_temp["longitude"] = lon
            data_list.append(data_temp)

    data = pd.concat(data_list, ignore_index=True)

    prediction_data = tomorrows_prediction_data(latitude, longitude)
    prediction_test = user_test_data(latitude, longitude)

    if prediction_data and prediction_test:
        lat    = prediction_data["latitude"]
        lon    = prediction_data["longitude"]
        daily  = prediction_data["daily"]
        prediction_list = pd.DataFrame(daily)

        prediction_list["latitude"]  = lat
        prediction_list["longitude"] = lon
        prediction_data = prediction_list.copy()

        lat    = prediction_test["latitude"]
        lon    = prediction_test["longitude"]
        daily  = prediction_test["daily"]
        prediction_list = pd.DataFrame(daily)

        prediction_list["latitude"]  = lat
        prediction_list["longitude"] = lon
        prediction_test = prediction_list.copy()

    else:
        raise RuntimeError(f'Dados indisponíves, tente novamente.')

    for dataframe in (data, prediction_data, prediction_test):
        dataframe["time"]        = pd.to_datetime(dataframe["time"])
        dataframe["day_of_year"] = dataframe["time"].dt.dayofyear
        dataframe["month"]       = dataframe["time"].dt.month
        dataframe["weekday"]     = dataframe["time"].dt.weekday
        dataframe["year"]        = dataframe["time"].dt.year

        dataframe.sort_values(["latitude", "longitude", "time"], inplace=True)
        dataframe.drop(columns="time", inplace=True)
        dataframe["weather_code"] = dataframe["weather_code"].apply(group_weather)

        dataframe["target_weather"] = dataframe.groupby(["latitude", "longitude"])["weather_code"].shift(-1)
        dataframe["target_temperature"] = dataframe.groupby(["latitude", "longitude"])["temperature_2m_mean"].shift(-1)
        
        for column in dataframe:
            if column in ["weather_code", "latitude", "longitude", "day_of_year", "month",
                          "weekday", "year", "target_weather", "target_temperature"]:
                continue
            dataframe[column+'_yesterday'] = dataframe.groupby(["latitude", "longitude"])[column].shift(1)
            dataframe[column+'_b4_yesterday'] = dataframe.groupby(["latitude", "longitude"])[column].shift(2)
        dataframe.replace({None: 0}, inplace=True)
        dataframe.reset_index(drop=True, inplace=True)

    train_data = data.dropna().copy()
    test_data = prediction_test.dropna().copy()

    # /----- Temperature Prediction Train -----/
    modelTemp = LinearRegression()
    x_train = train_data.drop(columns=["target_temperature", "target_weather"])
    y_train = train_data["target_temperature"]
    modelTemp.fit(x_train, y_train)

    # /----- Weather Prediction Train -----/
    counts  = data["weather_code"].value_counts()
    weights = {weight: counts.sum()/count for weight, count in counts.items()}
    modelWeather = RandomForestClassifier(class_weight=weights, random_state=67)
    x_train = train_data.drop(columns=["weather_code", "target_temperature", "target_weather"])
    y_train = train_data["weather_code"]
    modelWeather.fit(x_train, y_train)

    # /----- Testing model accuracy -----/
    x_test  = test_data.drop(columns=["target_temperature", "target_weather"])
    y_test  = test_data["target_temperature"]
    predT   = modelTemp.predict(x_test)
    margin  = root_mean_squared_error(y_test, predT)

    x_test  = test_data.drop(columns=["weather_code", "target_temperature", "target_weather"])
    y_test  = test_data["weather_code"]
    predW   = modelWeather.predict(x_test)
    precision = precision_score(y_test, predW, average='weighted')

    # /----- Temperature tomorrow's prediction -----/
    x_predT = prediction_data.drop(columns=["target_temperature", "target_weather"])
    predT   = modelTemp.predict(x_predT.tail(1))

    # /----- Weather tomorrow's prediction -----/
    x_predW = prediction_data.drop(columns=["weather_code", "target_temperature", "target_weather"])
    predW   = modelWeather.predict(x_predW.tail(1))

    return {
        "temperatures": int(predT[-1]), 
        "margin": ceil(margin), 
        "weather": weather_code[predW[-1]], 
        "precision": round(precision * 100, 2)
    }

def main():
    results = models(0, 0)
    print(results)

if __name__ == '__main__':
    main()
