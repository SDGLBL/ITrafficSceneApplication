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
    'task_name': '高速公路场景',
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
            'type': 'Yolov4Detector',
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
                'type': 'PathExtract',  # 路径分析模块，基础模块，不可或缺
            },
            {
                'type': 'TrafficStatisticsByStraight',  # 车流统计模块
                'is_process': False  # 是否开启该组件
            },
            {
                'type': 'ParkingMonitoringComponent', # 违章停车监控组件
                'monitoring_area': None, # 监控区域，必须赋值
                'allow_stop_time': TaskConfig.ALLOW_STOP_TIME,
                'is_process':False # 是否开启该组件
            },
            {
                'type': 'LaneMonitoringComponent', # 违法占用车道组件
                'monitoring_area':None,  # 监控区域，必须赋值
                'no_allow_car':None, # 比如{1:['car','truck']} 则在monitoring_area中值为1的区域内不允许出现car和truck
                'is_process':False # 是否开启该组件
            },
            {
                'type': 'PersonMonitoringComponent', # 违章停车监控组件
                'monitoring_area': None, # 监控区域，必须赋值
                'is_process':False # 是否开启该组件
            },
            # 数据库写入组件
            {
                'type': 'InformationCollectorComponent',
            },
            {
              'type': 'DrawBoundingBoxComponent'  # 画框框
            },
            {
                'type': 'RtmpWriteComponent',
                'resolution': (1920, 1080),
                'fps': 30,
                'rtmpUrl': TaskConfig.RTMP_URL
            }

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
    jsonname = filename.split('.')[0]+'.json'
    jsonpath = osp.join(DataConfig.JSON_DIR,jsonname)
    if not osp.exists(jsonpath):
        raise RuntimeError('文件夹{}中不存在名字为{}的json'.format(DataConfig.JSON_DIR, jsonname))
    taskCfg['head']['json_filename'] = jsonpath
    taskCfg['backbones'][0][2]['is_process'] = True
    if 'parking_monitoring_area' in cfg_data.keys():
        all_point_array = [np.array(x, dtype=np.int32) for x in cfg_data['parking_monitoring_area']]
        mask = np.ones_like(mmcv.VideoReader(filepath)[10][:,:,0])
        parking_mask = cv2.fillPoly(mask, all_point_array, 0)
        taskCfg['backbones'][0][3]['monitoring_area'] = parking_mask
        taskCfg['backbones'][0][3]['is_process'] = False
    if 'lane_monitoring_area' in cfg_data.keys():
        if 'lane_no_allow_cars' not in cfg_data.keys():
            raise RuntimeError('如果已经提供车道检测区域，请也提供禁止出现车辆信息')
        taskCfg['backbones'][0][4]['is_process'] = False
        lane_no_allow_cars = cfg_data['lane_no_allow_cars']
        all_point_array = [np.array(x, dtype=np.int32) for x in cfg_data['lane_monitoring_area']]
        mask = np.ones_like(mmcv.VideoReader(filepath)[10][:,:,0])
        for lane_area, no_allow_flag in zip(all_point_array, lane_no_allow_cars.keys()):
            mask = cv2.fillPoly(mask, [lane_area],int(no_allow_flag) )
        taskCfg['backbones'][0][4]['monitoring_area'] = mask
        taskCfg['backbones'][0][4]['no_allow_car'] = lane_no_allow_cars
    if 'person_monitoring_area' in cfg_data.keys():
        all_point_array = [np.array(x, dtype=np.int32) for x in cfg_data['person_monitoring_area']]
        mask = np.ones_like(mmcv.VideoReader(filepath)[10][:,:,0])
        new_mask = cv2.fillPoly(mask, all_point_array, 1)
        taskCfg['backbones'][0][5]['monitoring_area'] = new_mask
        taskCfg['backbones'][0][5]['is_process'] = True
    return taskCfg
