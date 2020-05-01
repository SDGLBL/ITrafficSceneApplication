import torch

from utils.buildline import Yolov3TaskBuilder

if __name__ == '__main__':
    components = {
        'head_detector':[
            {
                'type':'VideoFileHead',
                'filename':'./test.mp4',
                'step':16,
                'cache_capacity':100
            },
            {
                'type':'Yolov3Detector',
                'device':torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
                'batch_size':16
            }
        ],
        'backbones_components_cfgs':[
            [{
                'type':'WriteVideoBackboneComponent',
                'resolution':(1280,720),
                'fps':30
            }]
        ]
    }
    builder = Yolov3TaskBuilder(components=components)
    builder.start()

