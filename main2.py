import multiprocessing as mp
import torch
import platform
from utils.buildline.builder_q import YolovTaskBuilder

if __name__ == '__main__':
    mp.set_start_method('spawn',force=True)
    components = {
        'head_cfg': {
            'type': 'VideoFileHead',
            'filename': './test2.mp4',
            'step': 32,
            'cache_capacity': 10000
        }
        ,
        'detector_cfg': {
            'type': 'Yolov3Detector',
            'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
            'batch_size': 32
        },
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
                    'resolution': (1280, 720),
                    'fps': 30
                }
            ]
        ]
    }
    task = YolovTaskBuilder(components=components)
    task.start()