import torch
from cfg import Cfg
SaveImgInfoTaskCfg = {
    'head': [
        {
            'type': 'VideoFileHead',
            'filename': 'videoData/video/gta5_small.mp4',
            'step': Cfg.batch_size,
            'cache_capacity': 100
        }
    ],
    'detector': [
        {
            'type': 'Yolov4Detector',
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
                'type': 'SaveImgInfo',
                'savePath': 'videoData/json/gta5_small.json'
            }
        ]
    ]
}
