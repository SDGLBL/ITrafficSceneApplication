from multiprocessing import Queue,Process
from utils import get_logger
from ..registry import build_from_cfg
from components.registry import *
Loger = get_logger()
class BaseBuilder(object):

    def __init__(self,components):
        self.component = components
        self.head = None
        self.backbones = None
        self.build()

    def build(self):
        self.head_detector_cfg = self.component['head_detector']
        self.processing_backbones_cfg = self.component['processing_backbones']
        # 根据数据处理主干的长度创建多个进程通信队列，用于进程通信
        self.send_qs = [Queue(maxsize=100) for _ in range(len(self.processing_backbones_cfg))]
        self.head = self._build_head()
        self.backbones = self._build_backbones()

    def _build_head(self):
        def head_detector_component(hdcfg,send_qs):
            video_head = build_from_cfg(hdcfg[0],HEAD)
            detector = build_from_cfg(hdcfg[1],DETECTOR)
            img_shape = video_head[0].shape[:2]
            try:
                for imgs in video_head:
                    Loger.info("处理一条数据")
                    detections = detector(imgs, img_shape)
                    # 使用队列向body发送神经网络处理的数据
                    for send_q in send_qs:
                        send_q.put((video_head, detections),timeout=5)
            except:
                print('head_detector_component超时结束')
            finally:
                return
        return head_detector_component


    def _build_backbones(self):
        def backbones(bccfgs, reciveq):
            backbone_components = [build_from_cfg(bccfg) for bccfg in bccfgs]
            try:
                while True:
                    imgs, detections = reciveq.get(block=True, timeout=5)
                    kwargs = backbone_components[0].process({'imgs': imgs, 'detections': detections})
                    if len(backbone_components) > 1:
                        for backbone_component in backbone_components[1:]:
                            kwargs = backbone_component(kwargs)
            except KeyboardInterrupt:
                print(str(backbone_components) + '超时停止运行')
            finally:
                reciveq.close()
            return
        return backbones


    def start(self):
        head_p = Process(target=self.head,args=(self.head_detector_cfg,self.send_qs,))
        head_p.start()
        # 启动主干进程
        for backbone_components_cfg, reciveq in zip(self.processing_backbones_cfg, self.send_qs):
            backbone_p = Process(target=self.backbones,args=(backbone_components_cfg,reciveq,))
            backbone_p.start()
