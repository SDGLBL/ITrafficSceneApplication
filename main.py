import argparse
import torch
from components.detector import Yolov3Detector
from components.head import VideoFilePipeline
from components.backbones.vwriter import WriteVideoBackboneComponent
from utils import BaseBuilder
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch_size',default=8)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    components = {
        'head_detector':[
            {
                'type':'VideoFilePipeline',
                'filename':'./test.mp4',
                'step':3,
                'cache_capacity':100
            },
            {
                'type':'Yolov3Detector',
                'device':torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            }
        ],
        'processing_backbones':[
            {
                'type':'WriteVideoBackboneComponent',
                'resolution':(720,1280),
                'fps':30
            }
        ]
    }
    builder = BaseBuilder(components=components)
    builder.build()
    builder.start()

