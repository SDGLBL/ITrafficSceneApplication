from cfg import Cfg
import torch
ModellingTaskCfg2 = {
    'head': [
        {
            'type': 'VideoFileHead',
            'filename': './gta5_small.mp4',
            'step': Cfg.batch_size,
            'cache_capacity': 100
        }
    ],
    'detector': [
        {
            'type': 'Yolov3Detector',
            'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
            'batch_size': Cfg.batch_size
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
                'type': 'PathExtract'
            },
            {
                'type': 'SaveImgInfo',
                'savePath': './img_infogta5_small.json'
            }
        ]
    ]
}