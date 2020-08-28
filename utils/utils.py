import math
import random
import datetime
import time
import os
import cv2
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from copy import deepcopy
from hyperlpr import HyperLPR_plate_recognition
from components.detector.yolov5.utilsv5.general import xyxy2xywh, plot_one_box

def get_classes():
    # Bounding-box colors
    bbox_colors = {}
    fp = open('./components/detector/yolov3/data/coco.names', "r")
    classes = fp.read().split("\n")[:-1]
    return classes

def draw_label(
        bboxs,
        obj_confs,
        cls_confs,
        cls_preds,
        ids,
        img: np.ndarray,
        pass_count,
        bbox_colors,
        classes = get_classes()):
    """[summary]

    Args:
        bboxs (list): bboxs
        obj_confs (list): 每个bbox对应的object置信度list
        cls_confs (list): 每个bbox对应的分类置信度list
        cls_preds (list): 每个bbox对应的分类list
        ids ([type]): 每隔目标的id
        img (np.ndarray): 图像list
        pass_count (int): 车辆通行总数量
        bbox_colors (list): 图像颜色数组

    Returns:
        np.ndarray: 绘制后的图像
    """        
    thickness = len(img) // 200
    # img = deepcopy(img)
    cls2lable = {'car':'小汽车','bus':'巴士','truck':'卡车','person':'人',
    'bicycle':'自行车','motorbike':'摩托车','traffic light':'交通信号灯',
    }
    for bbox, obj_conf, cls_conf, cls_pred, id in zip(bboxs, obj_confs, cls_confs, cls_preds, ids):
        if cls_pred not in cls2lable.keys():
            continue
        if bbox is None:
            # 如果bbox为None说明这个目标
            continue

        # x1, y1, x2, y2 = bbox
        # x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        class_label = cls_pred
        color = bbox_colors[classes.index(cls_pred)]
        # cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
        if id is not None and id != 'None':
            put_str = 'type:{}'.format(cls_pred) + ' score:{0}'.format(str(cls_conf)[:4]) + 'target ID:{0}'.format(int(id))
        else:
            put_str = 'type:{}'.format(cls_pred) + ' score:{0}'.format(str(cls_conf)[:4])
        # img = paint_chinese_opencv(img,put_str,(x1,y1-50),(255,0,0))
        plot_one_box(bbox,img,label=put_str,color=color,line_thickness=thickness)
        # cv2.putText(img, put_str, (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
    # cv2.putText(img, 'carNumber:' + str(pass_count), (200, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)
    return img

def draw_illegal_label(
        bbox,
        obj_conf,
        cls_conf,
        cls_pred,
        id,
        img: np.ndarray,
        number_plate: str ):
    """[summary]

    Args:
        bbox (list): bbox
        obj_conf (float): bbox对应的object置信度
        cls_conf (float): bbox对应的分类置信度
        cls_pred (str): bbox对应的分类
        id (int): 目标的id
        img (np.ndarray): 图像list
        number_plate (str): 违规车辆车牌号

    Returns:
        np.ndarray: 绘制后的图像
    """        
    thickness = len(img) // 200
    img = deepcopy(img)
    # img = deepcopy(img)
    if bbox is None:
        # 如果bbox为None说明这个目标
        raise RuntimeError("绘制违规框必须需要目标的bbox")
    x1, y1, x2, y2 = bbox
    offset = 10
    x1, y1, x2, y2 = int(x1) - offset, int(y1) - offset , int(x2) + offset, int(y2) + offset
    cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), thickness)
    cls2lable = {'car':'小汽车','bus':'巴士','truck':'卡车','person':'人'}
    if number_plate is not None:
        put_str = '车辆类型:{}'.format(cls2lable[cls_pred]) + ' 置信度:{0}'.format(str(cls_conf)[:4]) + ' 车牌:{0}'.format(number_plate)
    else:
        put_str = '车辆类型:{}'.format(cls2lable[cls_pred]) + ' 置信度:{0}'.format(str(cls_conf)[:4])
    img = paint_chinese_opencv(img,put_str,(x1,y1-50),(255,0,0))
    # cv2.putText(img, put_str, (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0,0,255), 2)
    return img

def draw_illegal_label_for_person(
        bbox,
        obj_conf,
        cls_conf,
        cls_pred,
        id,
        img: np.ndarray):
    """[summary]

    Args:
        bbox (list): bbox
        obj_conf (float): bbox对应的object置信度
        cls_conf (float): bbox对应的分类置信度
        cls_pred (str): bbox对应的分类
        id (int): 目标的id
        img (np.ndarray): 图像list

    Returns:
        np.ndarray: 绘制后的图像
    """        
    thickness = len(img) // 200
    img = deepcopy(img)
    # img = deepcopy(img)
    if bbox is None:
        # 如果bbox为None说明这个目标
        raise RuntimeError("绘制违规框必须需要目标的bbox")
    x1, y1, x2, y2 = bbox
    offset = 10
    x1, y1, x2, y2 = int(x1) - offset, int(y1) - offset , int(x2) + offset, int(y2) + offset
    cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), thickness)
    cls2lable = {'person':'人'}
    put_str = '类型:{}'.format(cls2lable[cls_pred]) + ' 置信度:{0}'.format(str(cls_conf)[:4])
    img = paint_chinese_opencv(img,put_str,(x1,y1-50),(255,0,0))
    # cv2.putText(img, put_str, (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0,0,255), 2)
    return img



def draw_label_from_infer(
        infer_output,
        bbox_colors):
    """[summary]

    Args:

    Returns:
        np.ndarray: 绘制后的图像
    """
    results = []
    imgs = infer_output['imgs']
    imgs_info = infer_output['imgs_info']
    for img,img_info in zip(imgs,imgs_info):
        bboxs = [ target['bbox'] for target in img_info['objects']]
        obj_confs = [ target['obj_conf'] for target in img_info['objects']]
        cls_confs = [ target['cls_conf'] for target in img_info['objects']]
        cls_preds = [ target['cls_pred'] for target in img_info['objects']]
        ids  = [index for index,_ in enumerate(img_info['objects'])]
        results.append(draw_label(
            bboxs,
            obj_confs,
            cls_confs,
            cls_preds,
            ids,
            img,
            None,
            bbox_colors
        ))
    return results


def draw_mask(raw_img,save_path,poins):
    save_mask = np.zeros_like(raw_img)
    for lane_area in poins:
        new_mask = cv2.fillPoly(raw_img, [lane_area],(0,0,255)) 
    cv2.imwrite(save_path,new_mask)

def paint_chinese_opencv(im,chinese,pos,color):
    img_PIL = Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
    font = ImageFont.truetype('./fonts/msyhbd.ttc',30,encoding="utf-8")
    fillColor = color #(255,0,0)
    position = pos #(100,100)
    draw = ImageDraw.Draw(img_PIL)
    draw.text(position,chinese,font=font,fill=fillColor)
 
    img = cv2.cvtColor(np.asarray(img_PIL),cv2.COLOR_RGB2BGR)
    return img



def get_random_bbox_colors():
    """获取随机颜色，数量为传入的类别数量
    Args:

    Returns:

    """
    classes = get_classes()
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(classes))]
    return colors


def bbox2center(bbox):
    """将bbox转换为中心坐标点
    Arguments:
        bbox {list(int64)} -- [x1,y1,x2,y2]

    Returns:
        (int64,int64) -- bbox的中心坐标点
    """
    x_c = (bbox[0] + bbox[2]) // 2
    y_c = (bbox[1] + bbox[3]) // 2
    return x_c, y_c


def bbox_distance(bbox1, bbox2):
    """计算两个bbox之间的距离

    Arguments:
        bbox1 {list(int64)} -- [x1,y1,x2,y2]
        bbox2 {list(int64)} -- [x1,y1,x2,y2]

    Returns:
        float -- 距离
    """
    point1 = bbox2center(bbox1)
    point2 = bbox2center(bbox2)
    return point_distance(point1, point2)


def point_distance(point1, point2):
    """计算两点的距离
    Args:
        point1: 第一个点
        point2: 第二个点

    Returns:
        float -- 距离
    """
    return math.sqrt((point2[1] - point1[1]) ** 2 + (point2[0] - point1[0]) ** 2)


def get_sub_img(raw_img,bbox):
    """获取bbox范围内的图像

    Args:
        raw_img (np.ndarray): 原图像
        bbox (list): [x1, y1, x2, y2]

    Returns:
        np.ndarray: 切割出的小图像
    """    
    img_shape = raw_img.shape
    h = img_shape[0]
    w = img_shape[1]
    x1, y1, x2, y2 = [int(x) for x in bbox]
    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
    img = raw_img[max(y1-100,0):min(y2+100,h), max(x1-100,0):min(x2+50,w)]
    # img = raw_img[y1:y2,x1:x2]
    return img


def is_bbox_in_img(img,bbox):
    """判断一个目标是否已经全部进入了图像范围内

    Args:
        img (np.ndarray): 原图像]
        bbox (list): [x1, y1, x2, y2]

    Returns:
        if 目标全部在图像内:
            返回 True
        否则
            返回 False
    """    
    img_shape = img.shape
    h = img_shape[0]
    w = img_shape[1]
    x1, y1, x2, y2 = bbox
    # [1379.0, 240.0, 1497.0, 284.0]
    # 900 1600
    # print('---------------')
    # print(bbox)
    # print(h,w)
    # print('---------------')
    if x1 > 0 and x2 < w - 10 and y1 > 0 and y2 < h - 10:
        return True
    else:
        return False

def identify_number_plate(raw_img: np.ndarray, bbox):
    """
    识别车牌号码

    Arguments:
        raw_img {np.ndarray} -- 传入裁减后的汽车图像或者传入未裁减图像和需要识别的车辆的bbox

    Keyword Arguments:
        bbox {list(int)} -- 需要识别的目标（车辆）的bbox (default: {None})

    Returns:
        list -- 识别结果二维数组，包括有如下信息 车牌  置信度  车牌的bbox
        [['浙GD7X75', 0.9588068808828082, [298, 189, 555, 286]]]
    """
    assert len(bbox) == 4, 'bbox must is [x1,y1,x2,y2]'
    if bbox is not None:
        img = get_sub_img(raw_img,bbox)
        # 如果截取的车辆画面任何一个维度大小为0则直接不识别
        if img.shape[0] == 0 or img.shape[1] == 0:
            return None
        # 如果截取的车辆画面比例悬殊直接不识别
        if img.shape[0] / img.shape[1] > 5 or img.shape[0] / img.shape[1] < 1 / 5:
            return None
        # 如果截取到的车辆占整幅画面的占比低于3%则直接选择不识别
        if (img.shape[0] * img.shape[1]) / (raw_img.shape[0] * raw_img.shape[1]) < 0.03:
            return None
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        result = HyperLPR_plate_recognition(img)
        if len(result) > 0 and result[0][1] > 0.8:
            return result[0][0]
        else:
            return None


def get_current_time():
    """获取格式化时间
    Example: Year-month-day hour:minute:second

    Returns:
        str: 格式化的时间
    """    
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_time2time(format_time: str):
    """将格式化时间转换为时间戳

    Args:
        format_time (str): 格式化的时间 格式为 Year-month-day hour:minute:second

    Returns:
        time: 时间戳
    """    
    ts = time.strptime(format_time, "%Y-%m-%d %H:%M:%S")
    return time.mktime(ts)


def time2format_time(nomal_time: str):
    """将时间戳转换为格式化时间

    Args:
        nomal_time (str): 字符串化的时间戳

    Returns:
        str: 格式化时间
    """    
    format_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(nomal_time))
    return format_time


def path2source_path(path:str):
    """将文件路径，强制转换为http src路径

    Args:
        path (str): 文件路径

    Returns:
        [type]: [description]

    Example:
        >>> x = "\\static\\data\\criminal\\x.jpg" # windows platfom
        >>> x = path2source_path(x)
        >>> print(x) # /static/data/criminal/x.jpg
    """    
    path = path.replace(os.sep,'/')
    return path