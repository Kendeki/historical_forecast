import pandas as pd
from dataFormer import tomorrows_prediction_data, user_test_data
from sklearn.metrics import root_mean_squared_error, precision_score, confusion_matrix
from utils import load_data, prepare_dataframe, train_temp_model, train_weather_model, weather_code

def make_prediction_data(latitude, longitude):
    pd_data = tomorrows_prediction_data(latitude, longitude)
    pd_test = user_test_data(latitude, longitude)
    if not (pd_data and pd_test):
        raise RuntimeError("Dados indisponíves, tente novamente.")
    d1 = pd.DataFrame(pd_data["daily"]).assign(latitude=pd_data["latitude"], longitude=pd_data["longitude"])
    d2 = pd.DataFrame(pd_test["daily"]).assign(latitude=pd_test["latitude"], longitude=pd_test["longitude"])
    return d1, d2

def models(latitude: float, longitude: float):
    data = load_data()
    prediction_data, prediction_test = make_prediction_data(latitude, longitude)
    data, prediction_data, prediction_test = map(prepare_dataframe, [data, prediction_data, prediction_test])

    train_data = data.dropna().copy()
    test_data  = prediction_test.dropna().copy()

    modelTemp    = train_temp_model(train_data)
    modelWeather = train_weather_model(train_data)

    x_testT = test_data.drop(columns=["target_temperature","target_weather"])
    y_testT = test_data["target_temperature"]
    margin  = root_mean_squared_error(y_testT, modelTemp.predict(x_testT))

    x_testW = test_data.drop(columns=["weather_code","target_temperature","target_weather"])
    y_testW = test_data["weather_code"]
    precision = precision_score(y_testW, modelWeather.predict(x_testW), average="weighted")

    # MATRIZ DE CONFUSAO PARA VERIFICAR A PRECISAO DO MODELO
    # y_predW = modelWeather.predict(x_testW)
    # labels_present = sorted(y_testW.unique())
    # cm = confusion_matrix(y_testW, y_predW, labels=labels_present)
    # cm_df = pd.DataFrame(cm, index=[weather_code[i] for i in labels_present],
    #                            columns=[weather_code[i] for i in labels_present])
    # print("Confusion Matrix:\n", cm_df)

    predT = modelTemp.predict(prediction_data.drop(columns=["target_temperature","target_weather"]).tail(1))[-1]
    predW = modelWeather.predict(prediction_data.drop(columns=["weather_code","target_temperature","target_weather"]).tail(1))[-1]

    return {
        "mean_temperature": round(float(predT),2),
        "margin": round(margin, 2),
        "weather": weather_code[predW],
        "precision": round(precision*100, 2)
    }

def main():
    print(models(66.160507, -153.369141))

if __name__ == "__main__":
    main()
