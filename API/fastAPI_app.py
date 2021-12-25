import uvicorn
import requests
import json
import time
import sqlite3
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from databases import Database
from predictor import MyKueskiModel
from starlette.responses import RedirectResponse

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


# Read/loads model in memory. Waiting requets.
model = MyKueskiModel()


database = Database("sqlite:///feature_store_online.db")

@app.on_event("startup")
async def database_connect():
    await database.connect()


@app.on_event("shutdown")
async def database_disconnect():
    await database.disconnect()

# endpoint feature store.
@app.get("/online_feature_store/client_id={id}",tags=['online_feature_store'])
async def fetch_data(id: int):
    #TODO chequear la calidad de los datos.
    #TODO chequear que el usuario exista.
    #TODO imprimir headers attacks. Origen requests. Poner idealmente tokens.
    # query to get selected features.
    query = f"""SELECT   age
                , years_on_the_job
                , nb_previous_loans
                , avg_amount_loans_previous
                , flag_own_car
                FROM features_table where id = {id}"""
    # Espero el resultado de la base de datos.
    #TODO add timeout  exception.
    results = await database.fetch_all(query=query)
    # check if query is empty.
    if len(results) < 1:
        raise HTTPException(status_code=404, detail="User not found")
    # Otherwise:
    return  results[0]
# Endopoint credit risk.
@app.get("/credit_risk/client_id={id}",tags=["credit_risk"])
def home(id: int):
    # query to api for features.
    response = requests.get(url+f"/online_feature_store/client_id={id}")
    # consulta a base de datos para ver si existe el client_id con respecto a si tiene o no features.
    if response.status_code == 200:
        # get features as datafame to make predictions.
        response_dict = response.json()
        # From all information on json keep columns to feed model predictions.
        input_model = pd.DataFrame(response_dict,index=[0])[["age","years_on_the_job","nb_previous_loans","avg_amount_loans_previous","flag_own_car"]]
        # TODO chequear imputacion de columnas y enviarlas a la salida del json.
        label, proba = model.predict(input_model)
        return {"client_id": id,"label":int(label), "score":proba, "input_variables":response_dict}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/")
async def docs_redirect():
    return RedirectResponse(url='/docs')

if __name__ == "__main__":
    uvicorn.run("fastAPI_app:app")