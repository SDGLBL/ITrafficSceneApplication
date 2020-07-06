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
    'task_name': '路边违规停车场景',
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
            'type': 'Yolov3Detector',
            'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
            'batch_size': TaskConfig.BATCH_SIZE
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
                'type': 'ParkingMonitoringComponent',  # 违章停车监控组件
                'monitoring_area': None,  # 监控区域，必须赋值
                'allow_stop_time': TaskConfig.ALLOW_STOP_TIME,
                'is_process': False  # 是否开启该组件
            },
            # 数据库写入组件
            {
                'type': 'InformationCollectorComponent',
            },
            # {
            #     'type': 'DrawBoundingBoxComponent'  # 画框框
            # },
            # {
            #     'type': 'RtmpWriteComponent',
            #     'resolution': (1920, 1080),
            #     'fps': 30,
            #     'rtmpUrl': TaskConfig.RTMP_URL
            # }
        ]
    ]
}


def get_injected_cfg(cfg_data):
    if 'filename' not in cfg_data.keys():
        raise RuntimeError('注入数据必须指定filename参数，以确定处理的数据。')
    filename = cfg_data['filename']
    filepath = osp.join(DataConfig.VIDEO_DIR, filename)
    if not osp.exists(filepath):
        raise RuntimeError('文件夹{}中不存在名字为{}的视频或者视频源头'.format(DataConfig.VIDEO_DIR, filename))
    taskCfg = deepcopy(TaskCfg)
    taskCfg['head']['filename'] = filepath
    if 'parking_monitoring_area' in cfg_data.keys():
        all_point_array = [np.array(x, dtype=np.int32) for x in cfg_data['parking_monitoring_area']]
        mask = np.ones_like(mmcv.VideoReader(filepath)[10][:,:,0])
        parking_mask = cv2.fillPoly(mask, all_point_array, 0)
        taskCfg['backbones'][0][1]['monitoring_area'] = parking_mask
        taskCfg['backbones'][0][1]['is_process'] = True
    return taskCfg
