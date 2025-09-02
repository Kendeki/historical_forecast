import pandas as pd
from json import loads
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import root_mean_squared_error, precision_score
from dataFormer import tomorrows_prediction_data

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
            record = loads(line)
            lat    = record["latitude"]
            lon    = record["longitude"]
            daily  = record["daily"]
            data_temp = pd.DataFrame(daily)

            data_temp["latitude"]  = lat
            data_temp["longitude"] = lon
            data_list.append(data_temp)

    prediction_data = tomorrows_prediction_data(latitude, longitude)

    if prediction_data:
        lat    = prediction_data["latitude"]
        lon    = prediction_data["longitude"]
        daily  = prediction_data["daily"]
        data_temp = pd.DataFrame(daily)

        data_temp["latitude"]  = lat
        data_temp["longitude"] = lon
        prediction_list.append(data_temp)
        prediction_list = pd.DataFrame(prediction_list)

    data = pd.concat(data_list, ignore_index=True)

    for dataframe in (data, prediction_data):
        dataframe["time"]        = pd.to_datetime(dataframe["time"])
        dataframe['day_of_year'] = dataframe['time'].dt.dayofyear
        dataframe['month']       = dataframe['time'].dt.month
        dataframe['weekday']     = dataframe['time'].dt.weekday
        dataframe['year']        = dataframe['time'].dt.year

        dataframe = dataframe.sort_values(["latitude", "longitude", "time"])
        dataframe = dataframe.drop(columns="time")
        dataframe["weather_code"] = dataframe["weather_code"].apply(group_weather)

        dataframe["target_weather"] = dataframe.groupby(["latitude", "longitude"])["weather_code"].shift(-1)
        dataframe["target_temperature"] = dataframe.groupby(["latitude", "longitude"])["temperature_2m_mean"].shift(-1)
        
        for column in dataframe:
            if column == "weather_code":
                continue
            dataframe[column+'1'] = dataframe.groupby(["latitude", "longitude"])[column].shift(1)
            dataframe[column+'2'] = dataframe.groupby(["latitude", "longitude"])[column].shift(2)
        dataframe.replace({None: 0})

    size_train = int(data.shape[0]*0.8)
    size_data = int(prediction_data.shape[0]) - 1
    del data_list
    del prediction_list

    # /----- Temperature Prediction Train -----/

    modelTemp = LinearRegression()

    x_train = data.iloc[:size_train, :].drop(columns="target_temperature").dropna()
    x_test  = data.iloc[size_train:, :].drop(columns="target_temperature").dropna()
    y_train = data["target_temperature"].iloc[:size_train].dropna()
    y_test  = data["target_temperature"].iloc[size_train:].dropna()

    modelTemp.fit(x_train, y_train)
    precision = precision_score(predW, y_test, average='weighted')

    # /----- Weather Prediction Train -----/

    counts  = data["weather_code"].value_counts()
    weights = {weight: counts.sum()/count for weight, count in counts.items()}

    modelWeather = RandomForestClassifier(class_weight=weights, random_state=67)

    x_train = data.iloc[:size_train, 1:].dropna()
    x_test  = data.iloc[size_train:, 1:].dropna()
    y_train = data.iloc[:size_train, 0].dropna()
    y_test  = data.iloc[size_train:, 0].dropna()

    modelWeather.fit(x_train, y_train)

    # /----- Temperature tomorrow's prediction -----/

#    y_test = 
    margin = root_mean_squared_error(predT[:, 0], y_test.iloc[:, 0])


    # /----- Weather tomorrow's prediction -----/


    return {"temperatures": predT[-1], 
            "margin": margin, 
            "weather": weather_code[predW[-1]], 
            "precision": precision}

def main():
    results = models(0, 0)
    print(results)

if __name__ == '__main__':
    main()
