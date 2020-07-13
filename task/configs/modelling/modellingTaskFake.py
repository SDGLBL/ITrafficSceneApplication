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
    'task_name':'环境建模Fake',
    'head': 
        {
            'type': 'EquivalentHead',
            'filename': None,
            'json_filename': None,
            'step': 8,
            'cache_capacity': 100,
            'haveImg': False
        }
    ,
    'backbones': [
        [
            {
                'type': 'PathExtract'   # 路径分析模块，基础模块，不可或缺
            },
            {
                'type': 'Modelling',
                'mapSize':(1080,1920),
                'modelPath': None 
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
    emodelname = filename.split('.')[0] + '.emd'
    emodelpath = osp.join(DataConfig.EMODEL_DIR, emodelname)
    taskCfg['backbones'][0][1]['modelPath'] = emodelpath
    return taskCfg