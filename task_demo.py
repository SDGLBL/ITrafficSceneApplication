import multiprocessing as mp
import platform
from queue import Empty
from threading import Thread

from task.build import TaskBuilder
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
    readt = Thread(target=read_info_from_task, args=(mqs,))
    readt.start()
    readt.join()
    # from utils.dao import excute_sql,get_connection
    # connection = get_connection(host='localhost',user='lijie',password='8241660925',db='itsa')
    # excute_sql(
    #     connection,
    #     'INSERT INTO traffic (start_time_id,start_time,end_time,obj_type,number_plate) '
    #     'VALUES (%s,%s,%s,%s,%s)',
    #     ('2020-05-18 07:51:36 36', '2020-05-18 07:51:36', '2020-05-18 07:51:36', 'car', '浙DD13G2'),
    #     False
    # )
