import numpy as np


class BasePipeline(object):
    """
    管道基类：用于流式处理神经网络产生的数据
    """
    def __init__(self):
        pass

    def update(self,bboxs,img:np.ndarray):
        """

        Args:
            bboxs: 每个图像中的bbox list ,包含有[x1, y1, x2, y2, obj_conf, cls_conf, cls_pred]
            img: 图像
        Returns:
        """
        pass
            