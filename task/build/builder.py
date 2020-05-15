import time

from ..base import BaseBuild
from task.utils import build_process
from torch.multiprocessing import Process, Queue

class TaskBuilder(BaseBuild):
    def __init__(self, cfg,timeout=10, maxsize=30):
        super().__init__()
        self.cfg = cfg
        self.task_args =  []
        self.build(timeout,maxsize)

    def build(self,timeout, maxsize):
        detector_cfg = None
        if 'detector' in self.cfg.keys():
            detector_cfg = self.cfg['detector']
        tracker_cfg = None
        if 'tracker' in self.cfg.keys():
            tracker_cfg = self.cfg['tracker']
        if 'backbones' not in self.cfg.keys() or 'head' not in self.cfg.keys():
            raise AttributeError('task_cfg必须至少包含有head 和 backbone')
        head_cfg = self.cfg['head']
        backbones_cfg = self.cfg['backbones']
        if not isinstance(backbones_cfg, list):
            raise AttributeError('backbones_cfg必须为list')
        compile_list = [('head', head_cfg), ('detector', detector_cfg), ('tracker', tracker_cfg),
                        ('backbones', backbones_cfg)]
        # 过滤掉不存在的Task组件cfg
        compile_list = [task_component for task_component in compile_list if task_component[1] is not None]
        # 开始解析Task结构
        sendqs_list = []
        recivqs_list = []
        for i in range(len(compile_list)):
            task_component = compile_list[i][1]
            # 检查Task组件cfg
            if not isinstance(task_component, list) or len(task_component) == 0:
                raise AttributeError('TaskComponentCfg必须为list且非空')
            if i + 1 < len(compile_list):
                qnum = len(compile_list[i + 1][1])
                sendqs = [Queue(maxsize=maxsize) for _ in range(qnum)]
                sendqs_list.append(sendqs)
        sendqs_list.append(None)
        recivqs_list.append(None)
        for sendqs in sendqs_list:
            recivqs_list.append(sendqs)
        # 开始构建Task
        for tc, sendqs, recivq in zip(compile_list, sendqs_list, recivqs_list):
            # 每个组件都需要知道自己的获得数据的队列recivq  以及 发送数据到其他组件的sendqs 以及自生类型以及cfg
            # Task组件类型 head or detector or tracker or backbones
            tc_type = tc[0]
            tc_cfg = tc[1]
            self.task_args.append((tc_type, tc_cfg, recivq, sendqs, timeout))
            # self.task.append(build_process(tc_type, tc_cfg, recivq, sendqs, timeout))

    def start(self, join=False):
        for args in self.task_args:
            processes = build_process(*args)
            for p in processes:
                p.start()
        time.sleep(10)
