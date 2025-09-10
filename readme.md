# Historical Forecast

Projeto que utiliza modelos Machine Learning supervisionados para previsão do tempo no dia seguinte, utilizando a biblioteca scikit learn para o desenvolvimento do projeto.  
Foi utilizado modelos de LinearRegression para previsão de temperatura e RandomForestClassifier para previsão de status (chuva, neve, tempo limpo etc.). Como métricas, usa-se
margem de erro na temperatura, que em média não passa de 2°C, precision para as classificações, além de uma matriz de confusão que demonstra a veracidade do modelo.  
Os dados para treino e testes foram obtidos através das API's fornecidas pela [Open Meteo](https://open-meteo.com/).
