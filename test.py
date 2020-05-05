import cv2
import torch
from matplotlib import pyplot as plt

from components.backbones.registry import BACKBONE_COMPONENT
from components.head.registry import HEAD
from utils.registry import build_from_cfg

if __name__ == '__main__':
    """这只是一个演示脚本
       演示了从项目根目录读取test.mp4文件并写入到save.mp4文件
    """
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
            [
                {
                    'type':'DrawBoundingBoxComponent'
                },
                {
                    'type': 'WriteVideoComponent',
                    'resolution': (1280, 720),
                    'fps': 30
                }
            ]
        ]
    }
    video_head = build_from_cfg(components['head_detector'][0], HEAD)
    drawlabel = build_from_cfg(components['backbones_components_cfgs'][0][0], BACKBONE_COMPONENT)
    # vwriter = build_from_cfg(components['backbones_components_cfgs'][0][1],BACKBONE_COMPONENT)
    #
    # for index,imgs in enumerate(video_head):
    #     if index > 20 :
    #         break
    #     vwriter.process(imgs=imgs, detections=[None for _ in range(30)])
    from components import Yolov4Detector

    detector = Yolov4Detector(device=torch.device('cuda'), batch_size=3, img_size=608)
    import time

    img = cv2.imread('./dog.jpg')
    imgs = [img, img, img]
    shape = img.shape
    st = time.time()
    output = detector(imgs, shape)
    et = time.time()
    kwargs = drawlabel.process(imgs=imgs, detections=output)
    print(et - st)
    imgs = kwargs['imgs']
    plt.imshow(cv2.cvtColor(imgs[1], cv2.COLOR_BGR2RGB))
    plt.show()
