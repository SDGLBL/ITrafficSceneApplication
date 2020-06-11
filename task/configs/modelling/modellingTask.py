from cfg import TaskConfig
import torch
TaskCfg = {
    'task_name':'环境建模',
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
            {
                'type': 'PathExtract'   # 路径分析模块，基础模块，不可或缺
            },
            {
                'type': 'Modelling',
                'revise': False,
                'modelPath': None, # 保存路径
                'dataNum': 30000
            }
        ]
    ]
}