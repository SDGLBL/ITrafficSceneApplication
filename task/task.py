import time
from multiprocessing import Queue, Manager

from task.base import BaseBuild
from task.utils import build_process


class Task(BaseBuild):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.task_args = []
        self.manager = Manager()
        self.run_se = self.manager.Value(bool, True)
        self.pause_event = self.manager.Event()
        # 默认task正常运行
        self.pause_event.set()
        # 标记task是否被启动过
        self.is_start = False

    def build(self, timeout=10, maxsize=30):
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
            if not isinstance(task_component, (dict, list)):
                raise RuntimeError('TaskComponentCfg必须为list或者dict')
            if isinstance(task_component, list):
                if len(task_component) == 0:
                    raise RuntimeError('backbones不能为空')
            if i + 1 < len(compile_list):
                qnum = 1 if not isinstance(compile_list[i + 1][1], list) else len(compile_list[i + 1][1])
                sendqs = [Queue(maxsize=maxsize) for _ in range(qnum)]
                sendqs_list.append(sendqs)
        backbone_num = len(compile_list[-1][1])
        backbone2main = [Queue(maxsize=50) for _ in range(backbone_num)]
        # 通过如下操作使得发送与接受quenue错位
        # sendqs_list = [head2detector,detector2tracker,tracker2backbone,backbone2main]
        # recivqs_list = [None,head2detector,detector2tracker,tracker2backbone,backbone2main]
        sendqs_list.append(backbone2main)
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
        return backbone2main

    def start(self):
        """启动该Task,如果该Task已经被挂起则使用该函数将会唤醒该Task,但如果task已经被kill调用此方法将会抛出错误

        Raises:
            RuntimeError: 无法继续已经被杀死的Task
        """
        # 如果task还未构建和启动
        if not self.is_start:
            self.is_start = True
            # 默认Task是正常运行的
            for args in self.task_args:
                processes = build_process(*args, run_semaphore=self.run_se, pause_event=self.pause_event)
                for p in processes:
                    p.start()
            time.sleep(2)
        # 如果task已经成功启动过但被杀死了
        elif self.is_start and not self.run_se.value:
            raise RuntimeError('无法继续已经被杀死的Task')
        # 如果task已经被启动过但只是被挂起了
        else:
            self.pause_event.set()

    def kill(self):
        """杀死该Task,调用此方法后将无法再start该task
        """
        if not self.is_start:
            raise AttributeError('Task还未启动过，无法杀死')
        self.run_se.value = False

    def suspend(self):
        """挂起该Task，该task将会处于阻塞状态，直到再次调用start
        """
        if not self.is_start:
            raise AttributeError('Task还未启动过，无法挂起')
        self.pause_event.clear()

    def is_alive(self):
        """判断该task是否死亡,请注意由于task是通过启动多个进程运行组件
        而进程的结束必须要在访问到运行信号量的前提下才能正确退出，所以
        如果在调用kill方法后立刻调用is_alive虽然会返回False，但实际进程
        不一定已经被停止。
        """
        if self.is_start and self.run_se.value is False:
            return True
        else:
            return False
