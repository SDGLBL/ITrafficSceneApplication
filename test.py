import torch
from torch.multiprocessing import Process,Queue
from utils import Yolov3TaskBuilder
from utils.registry import build_from_cfg
from components.backbones.registry import BACKBONE_COMPONENT
from components.detector.registry import DETECTOR
from components.head.registry import HEAD


if __name__ == '__main__':
    # cuda 只支持由spawn产生的进程
    #multiprocessing.set_start_method('forkserver')
    components = {
        'head_detector':[
            {
                'type':'VideoFileHead',
                'filename':'./test.mp4',
                'step':30,
                'cache_capacity':100
            },
            {
                'type':'Yolov3Detector',
                'device':torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
                'batch_size':8
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
    video_head = build_from_cfg(components['head_detector'][0],HEAD)
    #detector = build_from_cfg(components['head_detector'][1],DETECTOR)
    vwriter = build_from_cfg(components['backbones_components_cfgs'][0][0],BACKBONE_COMPONENT)

    for index,imgs in enumerate(video_head):
        if index > 20 :
            break
        vwriter.process(imgs=imgs, detections=[None for _ in range(30)])



