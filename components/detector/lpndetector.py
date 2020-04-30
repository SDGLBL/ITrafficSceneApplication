from components.registry import DETECTOR
from .base import BaseDetector
from hyperlpr import HyperLPR_plate_recognition
import numpy as np


@DETECTOR.register_module
class LpnDetector(BaseDetector):
    """
    车牌探测与识别类
    """
    def __init__(self,batch_size=1):
        super(LpnDetector, self).__init__(HyperLPR_plate_recognition,batch_size)

    def preprocessing(self,imgs):
        imgs = super().preprocessing(imgs)
        # 由于车牌识别只需要处理一张图像，此处将图像取出并转换,(N,C,H,W) -> (W,H,C)
        img = imgs[0]
        img = np.transpose(img,(2,1,0))
        return img

    def __call__(self, imgs:np.ndarray, *args, **kwargs):
        img = self.preprocessing(imgs)
        return self.model(img)


