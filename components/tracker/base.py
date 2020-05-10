from components.detector.yolov3 import load_classes

class BaseTracker(object):
    def __init__(self):       
        pass
    def preprocessing(self,bboxs):
        pass

    def __call__(self, bboxs):
        """实现对物体的跟踪

        Arguments:
            bboxs {numpy.narray} -- 表示一帧中的目标，格式为[ [x1,y1,x2,y2,other_info], …… ]
            RETURN {numpy.narray} -- 返回添加id之后的目标，格式为[ [x1,y1,x2,y2,id,other_info],…… ]
        """        

        pass
