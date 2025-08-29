import json
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import root_mean_squared_error, precision_score

def models():

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

    with open("data.ndjson", "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            lat    = record["latitude"]
            lon    = record["longitude"]
            daily  = record["daily"]
            data_temp = pd.DataFrame(daily)

            data_temp["latitude"]  = lat
            data_temp["longitude"] = lon
            data_list.append(data_temp)

    data = pd.concat(data_list, ignore_index=True)

    data["time"]        = pd.to_datetime(data["time"])
    data['day_of_year'] = data['time'].dt.dayofyear
    data['month']       = data['time'].dt.month
    data['weekday']     = data['time'].dt.weekday
    data['year']        = data['time'].dt.year

    data = data.sort_values(["latitude", "longitude", "time"])
    data = data.drop(columns="time")
    data["weather_code"] = data["weather_code"].apply(group_weather)

    for column in data:
        if column == "weather_code":
            continue
        data[column+'1'] = data.groupby(["latitude", "longitude"])[column].shift(1)
        data[column+'2'] = data.groupby(["latitude", "longitude"])[column].shift(2)

    data = data.fillna(0)
    data = data.dropna()
    data = data.replace({None: 0})

    size_train = int(data.shape[0]*0.8)

    # /----- Temperature Prediction -----/

    temperatures = ["temperature_2m_mean"]

    modelTemp = LinearRegression()

    x_train = data.iloc[:size_train, :].drop(columns=temperatures)
    x_test  = data.iloc[size_train:, :].drop(columns=temperatures)
    y_train = data[temperatures].iloc[:size_train]
    y_test  = data[temperatures].iloc[size_train:]

    modelTemp.fit(x_train, y_train)
    predT = modelTemp.predict(x_test)
    rmce = root_mean_squared_error(predT[:, 0], y_test.iloc[:, 0])

    # /----- Weather Prediction -----/

    counts  = data["weather_code"].value_counts()
    weights = {weight: counts.sum()/count for weight, count in counts.items()}

    modelWeather = RandomForestClassifier(class_weight=weights, random_state=67)

    x_train = data.iloc[:size_train, 1:]
    x_test  = data.iloc[size_train:, 1:]
    y_train = data.iloc[:size_train, 0]
    y_test  = data.iloc[size_train:, 0]

    modelWeather.fit(x_train, y_train)
    predW = modelWeather.predict(x_test)
    prc   = precision_score(predW, y_test, average='weighted')

    return {"temperatures": predT[-1], 
            "margin": rmce, 
            "weather": weather_code[predW[-1]], 
            "precision": prc}

def main():
    results = models()
    print(results)

if __name__ == '__main__':
    main()
