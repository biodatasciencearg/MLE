from joblib import load
from sklearn.ensemble import RandomForestClassifier
from sklearn.base import BaseEstimator, TransformerMixin
from imblearn.pipeline import Pipeline as imbpipeline
import pandas as pd
#from custom_transformers import *
import pandera as pa

# Custom transformer 
# Define custom transformers. Column selector.
class FeatureSelector(BaseEstimator, TransformerMixin):
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X[self.columns]

class CheckFeature(TransformerMixin):
    # TODO read from a repository of schemas.
    def __init__(self, schema):

        self.schema = schema
        self.failure_cases = None

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        try:
            df = self.schema.validate(X, lazy=True)
            
        except pa.errors.SchemaErrors as err:
            
            print("Schema errors and failure cases:")
            print(err.failure_cases)
            self.failure_cases = err.failure_cases
        return X

class MyKueskiModel():
    def __init__(self):
        """instantiate model into memory. Waiting requests..."""
        with open('model_risk.joblib', 'rb') as handle:
            self.model = load(handle)
    # TODO add 
    def predict(self,array):
        """Return given an array, the label of prediction and score. 
        Score is the probability of default in a range 0-1000: 0 means a good client  whereas 1000 is a bad client.
        """
        #TODO pipeline taking into acccount quality over predictions. return value into a new columns.Inform imputation
        # fill na, etc.
        # get the label (0/1)
        label = self.model.predict(array)[0]
        # compute score 0-1000. 
        score = int(self.model.predict_proba(array)[0][1]*1000)
        return (label,score)
