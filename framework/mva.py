from sklearn.externals import joblib
from keras.models import load_model
import numpy as np
class ModelPredict:

  def GetProb(self, data):
    if not len(data) == 1: data = [data]
    if self.type == 'keras': 
      data = np.array(data)
      p = self.model.predict(data)[0]
    else:               p = self.model.predict_proba(data)[0]
    return p[0]
    

  def __init__(self, model, type = 'keras'):
    self.type = type
    if type == 'keras':
      self.model = load_model(model)
    else: 
      self.model = joblib.load(model)


