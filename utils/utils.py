from components.detector.yolov3 import rescale_boxes,load_classes
from matplotlib import pyplot as plt
import numpy as np
import random
import cv2
import logging



def draw_label(
        bboxs,
        img:np.ndarray,
        bbox_colors,
        classes=load_classes('./components/detector/yolov3/data/coco.names')):
    """
    绘制bbox
    Args:
        bboxs: bboxs
        img: 图像
        bbox_colors:　图像颜色数组
        classes: 类别数组

    Returns:
        绘制后的图像
    """
    thickness = len(img) // 400
    for bbox in bboxs:
        x1,y1,x2,y2,obj_conf,cls_conf,cls_pred = bbox
        x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
        class_label = classes[int(cls_pred)]
        color = bbox_colors[int(cls_pred)]
        cv2.rectangle(img,(x1,y1),(x2,y2),color,thickness)
        put_str = class_label+' '+str(cls_conf)[:4]
        cv2.putText(img,put_str,(x1,y1-5),cv2.FONT_HERSHEY_COMPLEX,1,color,2)
    return img


def get_random_bbox_colors(classes=load_classes('./components/detector/yolov3/data/coco.names')):
    """
    获取随机颜色，数量为传入的类别数量
    Args:
        classes:

    Returns:

    """
    # Bounding-box colors
    bbox_colors = []
    for _ in range(len(classes)):
        bbox_colors.append((random.randint(60,255),random.randint(50,255),random.randint(70,255)))
    return bbox_colors


def get_logger(
    level=logging.INFO,
    filename='log.txt'
    ,filemode="w"
    , format="%(asctime)s %(name)s:%(levelname)s:%(message)s"
    , datefmt="%d-%M-%Y %H:%M:%S"):

    logging.basicConfig(
        level=level,
        filename='log.txt',
        filemode="w",
        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
        datefmt="%d-%M-%Y %H:%M:%S")
    return logging.getLogger(__name__)