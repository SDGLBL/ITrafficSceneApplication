import multiprocessing as mp
import platform

from task.build import TaskBuilder
from task.configs.yolov3task import Yolov3TaskCfg
from task.configs.preheat import PreheatTaskCfg

if __name__ == '__main__':
    # Linux平台启动
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)
    task = TaskBuilder(PreheatTaskCfg)
    task.start()
