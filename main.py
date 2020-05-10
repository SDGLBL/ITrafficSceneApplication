import torch
import multiprocessing as mp
import platform
from utils.buildline import YolovTaskBuilder

if __name__ == '__main__':
    # Linux平台启动
    if platform.system() == 'Linux':
        mp.set_start_method('spawn')
    """程序运行例子
        从根目录读取视频，并建立探测任务并启动
    """    
    components = {
        'head_detector': [
            {
                'type': 'VideoFileHead',
                'filename': './test.mp4',
                'step': 8,
                'cache_capacity': 100
            },
            {
                'type': 'Yolov4Detector',
                'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
                'batch_size': 8
            }
        ],
        'backbones_components_cfgs': [
            [
                {
                    'type': 'DrawBoundingBoxComponent'
                },
                {
                    'type': 'FpsCollectorComponent',
                    'isPrint': True
                },
                {
                    'type': 'WriteVideoComponent',
                    'resolution': (1920, 1080),
                    'fps': 30
                }
            ]
        ]
    }
    task = YolovTaskBuilder(components=components)
    task.start()