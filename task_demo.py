import multiprocessing as mp
import platform
from queue import Empty
from threading import Thread
from task.build import TaskBuilder
from task.configs.yolov3task import Yolov3TaskCfg
from task.configs.preheat import PreheatTaskCfg
from task.configs.fakedemo import FakedTaskCfg

def read_info_from_task(mqs):
    try:
        while True:
            for mq in mqs:
                img_info = mq.get(timeout=5)
                print('探测到{}个目标'.format(len(img_info['objects'])))
    except Empty:
        print('主进程结束')

if __name__ == '__main__':
    # Linux平台启动
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)
    task = TaskBuilder(FakedTaskCfg)
    mqs = task.build()
    task.start()
    readt = Thread(target=read_info_from_task,args=(mqs,))
    readt.start()
    readt.join()
    
