import cv2

class BaseVideoPipeline(object):
    def __init__(self,step=1):
        self.step = step

    def get_shape(self):
        """
        返回视频的图像分辨率
        """
        pass

    def get_fps(self):
        """
        返回帧率
        """
        pass

