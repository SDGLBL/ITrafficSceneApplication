import multiprocessing as mp
import platform
from queue import Empty
from threading import Thread

import mmcv
import numpy as np

from task.build import TaskBuilder
from task.configs.crossRoadsTask import CrossRoadsTaskCfg
from task.configs.crossRoadsTaskFake import CrossRoadsTaskFakeCfg
from task.configs.saveImgInfoTask import SaveImgInfoTaskCfg
from task.configs.modellingTaskFake import ModellingTaskFakeCfg


def read_info_from_task(mqs):
    try:
        while True:
            for mq in mqs:
                img_info = mq.get(timeout=5)
    except Empty:
        print('主进程结束')

if __name__ == '__main__':
    # Linux平台启动
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)
    task = TaskBuilder(CrossRoadsTaskFakeCfg)
    mqs = task.build()
    task.start()
    readt = Thread(target=read_info_from_task, args=(mqs,))
    readt.start()
    readt.join()
