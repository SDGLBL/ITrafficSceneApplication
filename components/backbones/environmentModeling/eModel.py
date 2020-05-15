import pickle

class eModel():
    def __init__(self,**kwargs):
        self.sMap = kwargs['sMap']
        self.paths = kwargs['paths']
        self.eModelPathsRoot = 'components/backbones/environmentModeling/eModeldata/'     #模型根目录 
    
    def save(self, modelName='lot_15'):
        with open(self.eModelPathsRoot + modelName + '.emd', 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(modelPath):
        with open(modelPath, 'rb') as f:
            return pickle.load(f)


