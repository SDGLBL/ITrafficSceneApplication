import multiprocessing as mp
import platform
from queue import Empty
from threading import Thread

import mmcv
import numpy as np

from task.build import TaskBuilder
from task.configs.modelling import ModellingTaskCfg


def read_info_from_task(mqs):
    try:
        while True:
            for mq in mqs:
                img_info = mq.get(timeout=5)
    except Empty:
        print('主进程结束')


if __name__ == '__main__':
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)
    task = TaskBuilder(ModellingTaskCfg)
    mqs = task.build()
    task.start()
    readt = Thread(target=read_info_from_task, args=(mqs,))
    readt.start()
    readt.join()
