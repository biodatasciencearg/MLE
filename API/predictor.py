from joblib import load
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

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
