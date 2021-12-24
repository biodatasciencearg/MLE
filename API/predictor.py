from joblib import load
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

class MyKueskiModel():
    def __init__(self):
        """Cuando instancio el objeto y empieza a correr la API solo levanto una vez el modelo y 
        respondo frente  a los llamados."""
        with open('model_risk.joblib', 'rb') as handle:
            self.model = load(handle)
        
    def predict(self,array):
        return (self.model.predict(array)[0],self.model.predict_proba(array)[0][1])
