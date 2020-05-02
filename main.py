import torch

from utils.buildline import Yolov3TaskBuilder

if __name__ == '__main__':
    """程序运行例子
        从根目录读取视频，并建立探测任务并启动
    """    
    components = {
        'head_detector': [
            {
                'type': 'VideoFileHead',
                'filename': './test.mp4',
                'step': 16,
                'cache_capacity': 100
            },
            {
                'type': 'Yolov3Detector',
                'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
                'batch_size': 16
            }
        ],
        'backbones_components_cfgs': [
            [
                {
                    'type': 'DrawBoundingBoxComponent'
                },
                {
                    'type': 'WriteVideoComponent',
                    'resolution': (1280, 720),
                    'fps': 30
                }
            ]
        ]
    }
    task = Yolov3TaskBuilder(components=components)
    task.start()

