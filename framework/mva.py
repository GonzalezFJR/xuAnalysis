from sklearn.externals import joblib
class ModelPredict:

  def GetProb(self, data):
    if not len(data) == 1: data = [data]
    p = self.model.predict_proba(data)[0]
    return p[0]
    

  def __init__(self, model):
    self.model = joblib.load(model)


