from _queue import Empty

from torch.multiprocessing import Process, Queue

from components.backbones.registry import BACKBONE_COMPONENT
from components.detector.registry import DETECTOR
from components.head.registry import HEAD
from utils.logger import get_logger
from .base import BaseBuild
from ..registry import build_from_cfg

Loger = get_logger()


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
            imgs, detections = reciveq.get(timeout=10)
            # 首先由该管道内的第一个组件处理数据
            kwargs = backbone_components[0].process(imgs=imgs,detections=detections)
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



def head_detector_component(hdcfg, send_qs):
    """head_detector
    将head和detector整合在一起(一个进程内)，由于Windows上IO速度受到WindowsDefender影响速度，
    其运行速度会比Linux慢1/2左右

    Args:
        i (PID): 无意义，预留出来给torch.multiprocessing创建进程时传入pid用得
        hdcfg (dict): head and detector cfg 描述head和detector的cfg字典
        send_qs (list[Queue]): Queues,用于给各个backbone发送处理后的信息
    """
    Loger.info('head_detector {0} start'.format(hdcfg))
    video_head = build_from_cfg(hdcfg[0], HEAD)
    Loger.info('create ' + str(video_head)+' and which len is {}'.format(len(video_head)))
    detector = build_from_cfg(hdcfg[1], DETECTOR)
    Loger.info('create '+str(detector))
    img_shape = video_head[0].shape[:2]
    try:
        for imgs in video_head:
            detections = detector(imgs, img_shape)
            # 使用队列向body发送神经网络处理的数据
            for send_q in send_qs:
                send_q.put((imgs, detections),timeout=10)
    except Exception as e:
        Loger.exception(e)
    finally:
        del detector
        del video_head
        for send_q in send_qs:
            send_q.close()
            del send_q
        Loger.info('release source')
        return


class YolovTaskBuilder(BaseBuild):

    def __init__(self, components):
        self.component = components
        self.head = None
        self.backbones = None
        self.send_qs = []
        self.build()

    def build(self):
        global send_qs
        self.head_detector_cfg = self.component['head_detector']
        self.backbones_components_cfgs = self.component['backbones_components_cfgs']
        # 根据数据处理主干的长度创建多个进程通信队列，用于进程通信
        self.send_qs = [Queue() for _ in range(len(self.backbones_components_cfgs))]

    def start(self):
        head_detctor = Process(target=head_detector_component,args=(self.head_detector_cfg,[x for x in self.send_qs],))
        head_detctor.start()
        # 启动主干进程
        for backbone_components_cfg, reciveq in zip(self.backbones_components_cfgs,[x for x in self.send_qs]):
            backbone_p = Process(target=backbone, args=(backbone_components_cfg, reciveq,))
            backbone_p.start()


