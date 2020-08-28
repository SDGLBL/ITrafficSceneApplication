import cv2
import mmcv
import os
import json
import torch
import os.path as osp
import numpy as np
from copy import deepcopy
from cfg import TaskConfig
from cfg import DataConfig

TaskCfg = {
    'task_name': 'process video',
    'head': 
        {
            'type': 'VideoFileHead',
            'filename': None,
            'step': TaskConfig.BATCH_SIZE,
            'cache_capacity': 100
        }
    ,
    'detector': 
        {
            'type': 'Yolov5Detector',
            'device': '0',
            'batch_size': TaskConfig.BATCH_SIZE,
            'weights':'./components/detector/yolov5/weights/yolov5s.pt'
        }
    ,
    'tracker':
        {
            'type': 'SORT_Track'
        }
    ,
    'backbones': [
        [
            # fps计数组件
            {
                'type': 'FpsCollectorComponent',
                'isPrint': TaskConfig.IS_PRINT_FPS
            },
            {
                'type': 'PathExtract',  # 路径分析模块，基础模块，不可或缺
            },
            {
              'type': 'DrawBoundingBoxComponent'  # 画框框
            },
            {
                'type':'WriteVideoComponent',
                'resolution':None,
                'write_path':None,
                'fps':30
            },
            {
                'type':'ProcessCollectorComponent',
                'isPrint': TaskConfig.IS_PRINT_PROCESS
            }
        ]
    ]
}


def get_injected_cfg(cfg_data):
    if 'filepath' not in cfg_data.keys():
        raise RuntimeError('注入数据必须指定filename参数，以确定处理的数据。')
    # filename = cfg_data['filename']
    # filepath = osp.join(DataConfig.VIDEO_DIR, filename)
    filepath = cfg_data['filepath']
    filename = os.path.basename(filepath)
    if not osp.exists(filepath):
        raise RuntimeError('文件夹{}中不存在名字为{}的视频或者视频源头'.format(DataConfig.VIDEO_DIR, filename))
    taskCfg = deepcopy(TaskCfg)
    taskCfg['head']['filename'] = filepath
    taskCfg['backbones'][0][3]['resolution'] = cfg_data['resolution']
    taskCfg['backbones'][0][3]['write_path'] = cfg_data['write_path']
    return taskCfg
