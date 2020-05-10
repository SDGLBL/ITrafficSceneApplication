from multiprocessing import Lock

import numpy as np
import torch

from .yolov3 import load_classes


class BaseDetector(object):
    """
    探测器基类：用于探测出图像中的目标
    必须实现__call__方法
    """

    def __init__(self, model, device, batch_size=1):
        """

        Args:
            model: 模型
            device: cuda or cpu
            batch_size: 批处理大小
        """
        if batch_size <= 0:
            raise AssertionError('batch_size不能为0或者负数')
        if batch_size % 2 != 0 and batch_size != 1:
            raise AttributeError('batch_size必须为2的倍数')
        self.model = model
        self.device = device
        self.model.to(self.device)
        self.classes = load_classes('./components/detector/yolov3/data/coco.names')
        self.batch_size = batch_size
        self.pLock = Lock()

    
    def preprocessing(self,imgs:list):
        """
        图像预处理：将图像进行预处理以方便神经网络直接输入
        Args:
            imgs:图像矩阵，shape应该为(N,C,H,W)
        Returns:
            imgs:处理后的图像矩阵
        """
        if not isinstance(imgs,(list,np.ndarray)):
            raise AssertionError("imgs的类型为{0},要求的类型为list or np.ndarray".format(type(imgs)))
        if len(imgs) is not self.batch_size:
            raise AssertionError("传入的图像数量必须与batch_size匹配")
        return imgs

    def afterprocessing(self, detections: torch.Tensor, imgs_info:list):

        pass

    def __call__(self, imgs: np.ndarray, imgs_info:list, *args, **kwargs):

        pass
