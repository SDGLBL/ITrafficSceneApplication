import math
import random

import cv2
import numpy as np
from hyperlpr import HyperLPR_plate_recognition
from matplotlib import pyplot as plt
from components.detector.yolov3 import load_classes


def draw_label(
        bboxs,
        obj_confs,
        cls_confs,
        cls_preds,
        ids,
        img: np.ndarray,
        passCount,
        bbox_colors,
        classes=load_classes('./components/detector/yolov3/data/coco.names')):
    """
    绘制bbox
    Args:
        bboxs: bboxs,
        obj_confs:每个bbox对应的object置信度list
        cls_confs:每个bbox对应的分类置信度list
        cls_preds:每个bbox对应的分类id list
        img: 图像
        bbox_colors:　图像颜色数组
        classes: 类别数组

    Returns:
        绘制后的图像
    """
    thickness = len(img) // 200
    for bbox, obj_conf, cls_conf, cls_pred, id in zip(bboxs, obj_confs, cls_confs, cls_preds, ids):
        if bbox is None:
            # 如果bbox为None说明这个目标
            continue
        x1, y1, x2, y2 = bbox
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        class_label = classes[int(cls_pred)]
        color = bbox_colors[int(cls_pred)]
        cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
        if id is not None:
            put_str = class_label + ' ' + str(cls_conf)[:4] + ' {0}'.format(id)
        else:
            put_str = class_label + ' ' + str(cls_conf)[:4]
        cv2.putText(img, put_str, (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
    cv2.putText(img, 'carNumber:' + str(passCount), (200, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)
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
        bbox_colors.append((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    return bbox_colors


def bbox2center(bbox):
    """
    将bbox转换为中心坐标点
    Arguments:
        bbox {list(int64)} -- [x1,y1,x2,y2]

    Returns:
        (int64,int64) -- bbox的中心坐标点
    """
    x_c = (bbox[0] + bbox[2]) // 2
    y_c = (bbox[1] + bbox[3]) // 2
    return x_c, y_c


def bboxdistance(bbox1, bbox2):
    """
    计算两个bbox之间的距离

    Arguments:
        bbox1 {list(int64)} -- [x1,y1,x2,y2]
        bbox2 {list(int64)} -- [x1,y1,x2,y2]

    Returns:
        float -- 距离
    """
    x1_c, y1_c = bbox2center(bbox1)
    x2_c, y2_c = bbox2center(bbox2)
    return math.sqrt((y2_c - y1_c) ** 2 + (x2_c - x1_c) ** 2)


i = 1
j = 1

def identify_number_plate(img: np.ndarray, bbox=None):
    """
    识别车牌号码

    Arguments:
        img {np.ndarray} -- 传入裁减后的汽车图像或者传入未裁减图像和需要识别的车辆的bbox

    Keyword Arguments:
        bbox {list(int)} -- 需要识别的目标（车辆）的bbox (default: {None})

    Returns:
        list -- 识别结果二维数组，包括有如下信息 车牌  置信度  车牌的bbox
        [['浙GD7X75', 0.9588068808828082, [298, 189, 555, 286]]]
    """
    assert len(bbox) == 4, 'bbox must is [x1,y1,x2,y2]'
    if bbox is not None:
        img_shape = img.shape
        h = img_shape[0]
        w = img_shape[1]
        x1, y1, x2, y2 = bbox
        x1, y1, x2, y2 = max((0, x1)), max((0, y1)), max((0, x2)), max((0, y2))
        x1, y1, x2, y2 = min((h, x1)), min((w, y1)), min((h, x2)), min((w, y2))
        img = img[y1:y2, x1:x2]
        if img.shape[0] == 0 or img.shape[1] == 0:
            return None
        global i
        global j
        result = HyperLPR_plate_recognition(img)
        # plt.imsave('save/target{}.jpg'.format(j), img)
        j+=1
        if len(result) > 0 and result[0][1] > 0.95:
            # plt.imsave('target{}.jpg'.format(i), img)
            i += 1
            return result
        else:
            return None
    else:
        return HyperLPR_plate_recognition(img)
