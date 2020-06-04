from cfg import TaskConfig
import torch
ModellingTaskCfg = {
    'head': [
        {
            'type': 'VideoFileHead',
            'filename': './gta5_small.mp4',
            'step': TaskConfig.BATCH_SIZE,
            'cache_capacity': 100
        }
    ],
    'detector': [
        {
            'type': 'Yolov4Detector',
            'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
            'batch_size': TaskConfig.BATCH_SIZE
        }
    ],
    'tracker': [
        {
            'type': 'SORT_Track'
        }
    ],
    'backbones': [
        [
            {
                'type': 'PathExtract'   # 路径分析模块，基础模块，不可或缺
            },
            {
                'type': 'Modelling',
                'revise': False,
                'modelPath': None,
                'dataNum': 30000
            }
        ]
    ]
}