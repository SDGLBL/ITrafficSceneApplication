import numpy as np
from torch.nn import Module

class BaseDetector(object):
    """
    探测器基类：用于探测出图像中的目标
    """
    def __init__(self,model:Module,batch_size:int):
        if batch_size <= 0:
            raise AssertionError('batch_size不能为0或者负数')
        self.model = model
        self.batch_size = batch_size
    
    def __preprocessing(self,imgs:np.ndarray):
        """
        图像预处理：将图像进行预处理以方便神经网络直接输入
        Args:
            imgs:图像矩阵，shape应该为(N,C,H,W)
        Returns:
            imgs:处理后的图像矩阵
        """
        if not isinstance(imgs,np.ndarray):
            raise AssertionError("imgs的类型为{0},要求的类型为np.ndarray".format(type(imgs)))
        if len(imgs) is not self.batch_size:
            raise AssertionError("传入的图像数量必须与batch_size匹配")
        if imgs.ndim is not 4:
            raise AssertionError("imgs的shape为{0},要求的shape应该为(N,C,H,W)".format(imgs.shape))
        return imgs

    def __call__(self, imgs:np.ndarray,*args, **kwargs):
        imgs = self.__preprocessing(imgs)
        return self.model(imgs)

