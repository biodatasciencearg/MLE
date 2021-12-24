import uvicorn
import requests
import json
from fastapi import FastAPI
import time
import sqlite3
import pandas as pd


# defino la url donde estara la api.
url =  "http://127.0.0.1:8000"

description = """
KueskiCreditRisk API helps you evaluate clients. Computing Default probability or getting features/descriptors. 🚀

## Online Feature Store

You can **get features** for each client with a client_id.

## Credit Risk Score

You will be able to:

* **Default Probability**: return default probability and the Label o/1 given a user ID.

"""
tags_metadata = [
    {
        "name": "credit_risk",
        "description": "Retrieve probability of Default using a Random Forest estimator.",
    },
    {
        "name": "online_feature_store",
        "description": "the API gets 5 variables import to define the default probability.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://kueski_documentation.com/",
        },
    },
]

app = FastAPI(title="Kueski CreditRisk",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "eliasLopez@developer.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },openapi_tags=tags_metadata)

from predictor import MyKueskiModel

# Read/loads model in memory. Waiting requets.
model = MyKueskiModel()

# Endopoint credit risk.
@app.get("/credit_risk/client_id={id}",tags=["credit_risk"])
def home(id: int):
    # consulta a base de datos para ver si existe el client_id con respecto a si tiene o no features.
    # control sobre timeouts posible caida en servicio de feature store.
    response = requests.get(url+f"/online_feature_store/client_id={id}")
    # get features as datafame to make predictions.
    response_dict = response.json()
    # From all information on json keep columns to feed model predictions.
    input_model = pd.DataFrame(response_dict,index=[0])[["age","years_on_the_job","nb_previous_loans","avg_amount_loans_previous","flag_own_car"]]
    print(input_model)
    # TODO chequear imputacion de columnas y enviarlas a la salida del json.
    label, proba = model.predict(input_model)
    # consulta a base de datos para ver si existe el client_id con respecto a si tiene o no features.
    return {"client_id": id,"label":int(label), "predict_proba":float(proba)}



@app.get("/online_feature_store/client_id={id}",tags=['online_feature_store'])
def home(id: int):
    # creo la conexion.
    #TODO chequear la calidad de los datos.
    #TODO chequear que el usuario exista.
    #TODO imprimir headers attacks. Origen requests. Poner idealmente tokens.
    cnx = sqlite3.connect('feature_store_online.db')
    query = f"""SELECT   age
                , years_on_the_job
                , nb_previous_loans
                , avg_amount_loans_previous
                , flag_own_car
                FROM features_table where id = {id}"""
    features = pd.read_sql_query(query, cnx)
    # Lo mando a un diccionario.
    features = features.iloc[0].to_dict()
    # Agrego el id
    features['id'] = id
    # cierro la conexion.
    cnx.close()
    # devuelvo el json con las features y el id.
    return features
  

if __name__ == "__main__":
    uvicorn.run("fastAPI_app:app")