import torch
from cfg import Cfg
Yolov3TaskCfg = {
    'head': [
        {
            'type': 'VideoFileHead',
            'filename': './test.mp4',
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
    'backbones': [
        [
            {
                'type': 'DrawBoundingBoxComponent'  # 画框框
            },
            {
                'type': 'FpsCollectorComponent',
                'isPrint': Cfg.is_print_fps
            },
            {
                'type': 'WriteVideoComponent',
                'resolution': (1920, 1080),
                'fps': 30
            }
        ]
    ]
}
