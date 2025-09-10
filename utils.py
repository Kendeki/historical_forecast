import pandas as pd
from json import loads
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier

def group_weather(code):
    if code == 0: return 0
    elif code in [1,2,3]: return 1
    elif code in [45,48]: return 2
    elif code in [51,53,55,56,57]: return 3
    elif code in [61,63,65,66,67,80,81,82]: return 4
    elif code in [71,73,75,77,85,86]: return 5
    elif code in [95,96,99]: return 6

weather_code = {
    0: "Clear Sky",
    1: "Cloudy",
    2: "Fog",
    3: "Drizzle",
    4: "Rain",
    5: "Snow",
    6: "Thunderstorm"
}


def prepare_dataframe(df):
    df["time"]        = pd.to_datetime(df["time"])
    df["day_of_year"] = df["time"].dt.dayofyear
    df["month"]       = df["time"].dt.month
    df["weekday"]     = df["time"].dt.weekday
    df["year"]        = df["time"].dt.year
    df["weather_code"] = df["weather_code"].apply(group_weather)
    df.sort_values(["latitude", "longitude", "time"], inplace=True)
    df.drop(columns="time", inplace=True)
    df["target_weather"] = df.groupby(["latitude", "longitude"])["weather_code"].shift(-1)
    df["target_temperature"] = df.groupby(["latitude", "longitude"])["temperature_2m_mean"].shift(-1)
    for column in df:
        if column in ["weather_code","latitude","longitude","day_of_year","month","weekday","year","target_weather","target_temperature"]:
            continue
        df[column+"_yesterday"] = df.groupby(["latitude","longitude"])[column].shift(1)
        df[column+"_b4_yesterday"] = df.groupby(["latitude","longitude"])[column].shift(2)
    df.replace({None:0}, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def load_data():
    with open("data.ndjson","r",encoding="utf-8") as f:
        data = [pd.DataFrame(loads(line)["daily"]).assign(
            latitude=loads(line)["latitude"], longitude=loads(line)["longitude"]) for line in f]
    return pd.concat(data, ignore_index=True)

def train_temp_model(train_data):
    x = train_data.drop(columns=["target_temperature","target_weather"])
    y = train_data["target_temperature"]
    return LinearRegression().fit(x,y)

def train_weather_model(train_data):
    x = train_data.drop(columns=["weather_code","target_temperature","target_weather"])
    y = train_data["weather_code"]
    return RandomForestClassifier(class_weight="balanced", random_state=67).fit(x,y)
