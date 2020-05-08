from queue import Empty
import torch
from torch.multiprocessing import Process, Queue
from torch import multiprocessing
from components.backbones.registry import BACKBONE_COMPONENT
from components.detector.registry import DETECTOR
from components.head.registry import HEAD
from components.tracker.registry import TRACKER
from utils.logger import get_logger
from .base import BaseBuild
from ..registry import build_from_cfg
import time
import numpy as np
Loger = get_logger()    # 写入日志文件

def head_component(cfg, send_qs):
    """head_component:head组建构建器

    Arguments:
        cfg (dict):描述head的cfg字典
        send_qs (list[Queue]): Queues,一般只有检测器一个下游进程，发送的信息为(imgs,img_shape)
    """    
    Loger.info('head_component {0} start'.format(cfg))
    video_head = build_from_cfg(cfg, HEAD)
    img_shape = video_head[0].shape[:2]
    Loger.info('create ' + str(video_head)+' and which len is {}'.format(len(video_head)))
    try:
        for imgs in video_head:
            for send_q in send_qs:
                send_q.put((imgs, img_shape),timeout=10)
    except Exception as e:
        Loger.exception(e)
    finally:
        del video_head
        for send_q in send_qs:
            send_q.close()
            del send_q
        Loger.info('release source')
        return

def detector_component(cfg, reciveq, send_qs):
    """detector_component:检测器组建构建

    Arguments:
    cfg {dict} -- 描述detector的cfg字典
    reciveq {Pipe} -- 信息流入接口，用于用于接收来自head的图片数据流,信息输入格式为(imgs, None)
    send_qs {list[Queue]} -- Queues,向主干进程发送数据，数据格式为(imgs, detections)
    """    
    Loger.info('detector_component {0} start'.format(cfg))
    detector = build_from_cfg(cfg, DETECTOR)
    Loger.info('create '+str(detector))
    try:
        while True:
            # print(reciveq.qsize())
            imgs,img_shape = reciveq.get(timeout=10)
            detections = detector(imgs, img_shape)
            # print(detections)
            # print('-------------------')
            for send_q in send_qs:
                send_q.put((imgs, detections), timeout=10)
    except Exception as e:
        Loger.exception(e)
    finally:
        del detector
        torch.cuda.empty_cache()
        for send_q in send_qs:
            send_q.close()
            del send_q
        Loger.info('release source')
        return

def tracker_component(cfg, reciveq, send_qs):
    """跟踪组件

    Arguments:
        cfg {dict} -- 描述跟踪器参数
        reciveq {Pipe} -- 信息流入接口，用于用于接收来自detector的图片数据流,信息输入格式为(imgs, detection)
        send_qs {list[Queue]} -- Queues,向主干进程发送数据，数据格式为(img, bboxs)
                                 (注，发送为单帧图像而非图片组，bboxs为以类名为key的dict格式,详情请见components.tarcker.SORT_Track类的具体实现)
    """    
    Loger.info('tracker_component {0} start'.format(cfg))
    tracker = build_from_cfg(cfg, TRACKER)
    Loger.info('create '+str(tracker))
    try:
        while True:
            [imgs, detections] = reciveq.get(timeout=100)
            # 取出每一帧的img, bboxs，进行追踪操作，并逐帧发送到下一个进程
            for i in range(len(imgs)):
                bboxs = tracker(detections[i])
                if bboxs is not None:
                    for class_name in bboxs:
                        print(class_name + str(bboxs[class_name].astype(int)))
                for send_q in send_qs:
                    send_q.put((imgs[i], bboxs), timeout=100)
    except Exception as e:
        Loger.exception(e)
    finally:
        del tracker
        for send_q in send_qs:
            send_q.close()
            del send_q
        Loger.info('release source')
        return

def backbone(bccfgs, reciveq):
    """backbone
    每个backbone占用一条进程，处理一种或多种任务

    Args:
        bccfgs ([list[dict]]): backbone components cfgs 一个list其中每个元素都是一个component的cfg dict
        reciveq (Pipe): 管道,用于接收来自head_detecotr 或者 detector的数据
    """
    Loger.info('backbone {0} start'.format(bccfgs))
    backbone_components = [build_from_cfg(bccfg, BACKBONE_COMPONENT) for bccfg in bccfgs]
    try:
        while True:
            img, bboxs = reciveq.get(timeout=100)
            # 首先由该管道内的第一个组件处理数据
            kwargs = backbone_components[0].process(img=img,bboxs=bboxs)
            if not isinstance(kwargs,dict):
                raise AttributeError('每个组件处理后返回的数据必须为字典')
            if len(backbone_components) > 1:
                # 如果该管道有多个component的话依次将数据交给之后的component处理
                for backbone_component in backbone_components[1:]:
                    kwargs = backbone_component.process(**kwargs)
                # 处理到最后的数据直接清楚(非必须)
            del kwargs
        Loger.info('backbone {0} stoped'.format(bccfgs))
    except Empty as epe:
        Loger.info('backbone normal stoped')
    except Exception as e:
        Loger.exception(e)
    return



class YolovTaskBuilder(BaseBuild):

    def __init__(self, components):
        self.component = components
        self.head = None
        self.backbones = None
        self.send_qs = []
        self.build()

    def build(self):
        self.head_cfg = self.component['head_cfg']
        self.detector_cfg = self.component['detector_cfg']
        self.tracker_cfg = self.component['tracker_cfg']
        self.head_to_detector_q = Queue(maxsize = 10)
        self.detector_to_tracker_q = Queue(maxsize = 50)
        self.backbones_components_cfgs = self.component['backbones_components_cfgs']
        self.send_qs = [Queue() for _ in range(len(self.backbones_components_cfgs))]

    def start(self):
        head = Process(target=head_component,args=(self.head_cfg, [self.head_to_detector_q]))
        detector = Process(target=detector_component, args=(self.detector_cfg, self.head_to_detector_q, [self.detector_to_tracker_q]))
        tracker = Process(target=tracker_component, args=(self.tracker_cfg, self.detector_to_tracker_q, self.send_qs))

        head.start()
        detector.start()
        tracker.start()

        # 启动主干进程
        for backbone_components_cfg, reciveq in zip(self.backbones_components_cfgs,[x for x in self.send_qs]):
            backbone_p = Process(target=backbone, args=(backbone_components_cfg, reciveq,))
            backbone_p.start()

        time.sleep(10)

