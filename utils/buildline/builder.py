from torch.multiprocessing import Process,Pipe
from torch import multiprocessing
from ..registry import build_from_cfg
from components.backbones.registry import BACKBONE_COMPONENT
from components.detector.registry import DETECTOR
from components.head.registry import HEAD
from .base import BaseBuild
from utils import get_logger
import numpy as np



def backbones(bccfgs, reciveq):
    Loger = get_logger('./backbones.txt')
    backbone_components = [build_from_cfg(bccfg, BACKBONE_COMPONENT) for bccfg in bccfgs]
    try:
        while True:
            imgs, detections = reciveq.recv()
            kwargs = backbone_components[0].process(imgs=imgs,detections=detections)
            if len(backbone_components) > 1:
                for backbone_component in backbone_components[1:]:
                    kwargs = backbone_component(kwargs)
    except KeyboardInterrupt:
        Loger.warning(msg='手动停止')
    finally:
        reciveq.close()
    return


def head_detector_component(i,hdcfg, send_qs):
    Loger = get_logger(filename='head_log.txt')
    Loger.info('head process start')
    video_head = build_from_cfg(hdcfg[0], HEAD)
    Loger.info('create ' + str(video_head)+' and which len is {}'.format(len(video_head)))
    detector = build_from_cfg(hdcfg[1], DETECTOR)
    Loger.info('create '+str(detector))
    img_shape = video_head[0].shape[:2]
    i = 0
    try:
        for imgs in video_head:
            i += len(imgs)
            detections = detector(imgs, img_shape)
            # 使用队列向body发送神经网络处理的数据
            for send_q in send_qs:
                send_q.send((imgs, detections))
            print(i)
            if i % (len(imgs) * 50) == 0:
                Loger.info('当前处理进度为{}%'.format(i*100/len(video_head)))
    except:
        Loger.warning('head_detector_component结束运行,PS:这是正常现象')
    finally:
        return



class Yolov3TaskBuilder(BaseBuild):

    def __init__(self,components):
        self.component = components
        self.head = None
        self.backbones = None
        self.build()
        self.send_qs = []

    def build(self):
        global send_qs
        self.head_detector_cfg = self.component['head_detector']
        self.backbones_components_cfgs = self.component['backbones_components_cfgs']
        # 根据数据处理主干的长度创建多个进程通信队列，用于进程通信
        self.send_qs = [Pipe() for _ in range(len(self.backbones_components_cfgs))]


    def start(self):
        ctx = multiprocessing.spawn(
            head_detector_component,
            args=(self.head_detector_cfg,[x[0] for x in self.send_qs],),
            join=False)
        # 启动主干进程
        for backbone_components_cfg, reciveq in zip(self.backbones_components_cfgs,[x[1] for x in self.send_qs]):
            backbone_p = Process(target=backbones,args=(backbone_components_cfg,reciveq,))
            backbone_p.start()
        ctx.join()
