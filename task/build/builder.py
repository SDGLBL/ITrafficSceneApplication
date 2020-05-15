import time

from ..base import BaseBuild
from ..utils import compile_task_cfg


class TaskBuilder(BaseBuild):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.task = None
        self.build()

    def build(self):
        self.task = compile_task_cfg(self.cfg)

    def start(self, join=False):
        last_c = None
        for task_components in self.task:
            for component in task_components:
                component.start()
                last_c = component
        if join:
            last_c.join()
        else:
            time.sleep(10)
