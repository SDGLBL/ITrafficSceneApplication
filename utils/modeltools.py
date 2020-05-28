# 用于方便.emd模型的使用的工具函数文件

import pickle
import os
from .analysistools import *
import numpy as np

def emdLoad(filePath):
    with open(filePath, 'rb') as f:
        model = pickle.load(f)
        print(model)
    if not isinstance(model,dict):
        print('错误的.emd文件')
        return None
    if 'type' not in model.keys():
        print('错误的.emd文件')
        return None
    print(model)
    return model

def dotStatus(dot, emd):
    status = dotByLine(dot, emd['stop_line'], emd['avg_bbox']/10)
    return status

def pathsStatus(path, emd, lenTh=30):
    path = straighten(path, emd['avg_bbox']/10)
    if len(path['zipDots']) < lenTh:    # 如果路径太短则判定为无法判断
        return None
    path = pathFitting(path, emd['inv_transform_mat'])
    lane = emd['lane_classifier'].predict([[path['fun_dots'][0, 1]]])[0]
    dir = emd['dir_classifier'].predict([[path['fun_dots'][-1, 1]]])[0]
    return (lane, dir)

def isPass(path, emd):
    dots = path['dots']
    dots = np.array(dots)
    startDot = dots[0]
    farI = np.unravel_index(np.argmin(dots[:,1]),dots[:,1].shape)[0]
    endDot = dots[farI]
    half1 = dotByLine(startDot, emd['stop_line'], emd['avg_bbox']/10)
    half2 = dotByLine(endDot, emd['stop_line'], emd['avg_bbox']/10)
    if half1 == -1 and half2 != half1:
        return True
    else:
        return False

def dotByLine(dot, line, th):
    k, b = line
    if k*dot[0] + b - dot[1] > th:
        return 1
    elif k*dot[0] + b - dot[1] < -th:
        return -1
    else:
        return 0

def isInSidewalk(dot, emd):
    status1 = dotByLine(dot, emd['stop_line'], 0)
    line2 = [emd['stop_line'][0], emd['stop_line'][1]-emd['avg_bbox']]
    status2 = dotByLine(dot, line2, 0)
    if status1 != status2:
        return True
    else:
        return False
