import multiprocessing as mp
import torch
import platform
from utils.buildline.builder_2 import YolovTaskBuilder

if __name__ == '__main__':
    mp.set_start_method('spawn',force=True)
    components = {
        'head_cfg': {
            'type': 'VideoFileHead',
            'filename': './test.mp4',
            'step': 32,
            'cache_capacity': 200
        },
        'detector_cfg': {
            'type': 'Yolov3Detector',
            'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
            'batch_size': 32
        },
        'tracker_cfg': {
            'type': 'SORT_Track'
        },
        'backbones_components_cfgs': []
    }
    task = YolovTaskBuilder(components=components)
    task.start()

"""
[
                {
                    'type': 'DrawBoundingBoxAndIdComponent'
                },
                {
                    'type': 'WriteIdVideoComponent',
                    'resolution': (1280, 720),
                    'fps': 30,
                    'fourcc': 'MJPG',
                    'write_path': './save.avi'
                }
            ]
"""