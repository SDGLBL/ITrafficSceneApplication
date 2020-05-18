import multiprocessing as mp
import platform
from queue import Empty
from threading import Thread

from task.build import TaskBuilder
from task.configs.fakeinfo import FakedTaskCfg


def read_info_from_task(mqs):
    try:
        while True:
            for mq in mqs:
                img_info = mq.get(timeout=5)
                # print('探测到{}个目标'.format(len(img_info['objects'])))
    except Empty:
        print('主进程结束')

if __name__ == '__main__':
    # Linux平台启动
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)
    # FakedTaskCfg是一个虚假数据流通过读取已经生成好的json文件来模拟交通场景的实时数据流
    # 默认往数据库写入数据，如过不需要请自行注释对应组件
    task = TaskBuilder(FakedTaskCfg)
    mqs = task.build()
    task.start()
    readt = Thread(target=read_info_from_task, args=(mqs,))
    readt.start()
    readt.join()
