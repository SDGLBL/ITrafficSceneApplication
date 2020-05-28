import torch
from cfg import Cfg
CrossRoadsTaskCfg = {
    'head': [
        {
            'type': 'VideoFileHead',
            'filename': 'videoData/video/lot_15.mp4',
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
                'type': 'PathExtract'   # 路径分析模块，基础模块，不可或缺
            },
            {
                'type': 'TrafficStatistics'     # 车流统计模块
            }
        ]
    ]
}
