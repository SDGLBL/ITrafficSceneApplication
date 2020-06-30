import importlib
import os
from os.path import exists
from os.path import join
from queue import Empty
import time
import numpy as np
from threading import Thread
from cfg import TaskConfig, DataConfig
from task.task import Task
from .infopool import ImgInfoPool
from utils.logger import get_logger


def read_info_from_task(mqs, task_name: str, info_pool: ImgInfoPool):
    print('{} Task的读取信息线程启动'.format(task_name))
    try:
        while True:
            for mq in mqs:
                img_info = mq.get(timeout=5)
                info_pool.add(task_name=task_name, img_info=img_info)
                for analysis_info in img_info['analysis']:
                    if analysis_info['info_type'] != 'pass' and TaskConfig.IS_PRINT_ANALYSIS_INFO:
                        # 此处删除掉图像再显示，否则终端显示图像太长
                        del analysis_info['imgs']
                        print(analysis_info)
    except Empty:
        print('{} Task的读取信息线程停止'.format(task_name))
        for mq in mqs:
            mq.cancel_join_thread()
        return


class TaskManager(object):
    def __init__(self, info_pool: ImgInfoPool, config_dir=TaskConfig.SCENE_CFG_DIR):
        super().__init__()
        # self.tasks:[
        #   { 
        #   'task_name':task名字 Example:lot_15.mp4
        #   'task_snapshot_url':task处理的视频的截图 Example:/static/data/video/lot_15.jpg
        #   'task_progress':task处理的进度,范围为[0-100] Example:20
        #   }
        # ...]
        self.config_dir = config_dir
        self.tasks = {}
        # TODO: 添加task实时信息刷新字典，方便前端api获取tak执行情况
        self.logger = get_logger('logs/task.log')
        self.info_pool = info_pool

    def submit(self, task_name: str, task_cfg: dict):
        """提交一个Task
        Args:
            task_name: task的名字，需要保证不重复，其会作为task的唯一标识符，建议传入视频或摄像头名称
            task_cfg: task的数据字典
        Returns:
            返回是否返回值
        """
        # 如果超过了最多的提交数量限制
        if len(self.tasks) >= TaskConfig.MAX_TASK_NUM:
            raise RuntimeError("超过了最多的提交数量限制".format(task_name))
        if self.is_exist(task_name):
            raise RuntimeError("请勿重复提交task_name为{}的Task任务".format(task_name))
        task = Task(task_cfg)
        task.build()
        self.tasks[task_name] = task

    def is_exist(self, task_name: str):
        """检查指定的task是否已经存在

        Args:
            task_name (str): task的名字(处理的视频或者视频源的名字) Example：lot_15.mp4
        Returns:
            Boolen:存在返回True否则返回False
        """
        if task_name in self.tasks.keys():
            return True
        else:
            return False

    def suspend(self, task_name):
        """挂起指定的task，使其暂停运行，调用此函数后请确保能够再
        有限时间内杀死或重新启动该Task，否则可能导致进程死锁

        Args:
            task_name (str): task的名字(处理的视频或者视频源的名字) Example：lot_15.mp4

        Returns:
            Boolen:存在返回True否则返回False
        """
        if task_name in self.tasks.keys():
            self.tasks[task_name].suspend()
        else:
            raise RuntimeError('TaskManger中不存在名字为{}的task'.format(task_name))

    def kill(self, task_name):
        """直接杀死指定的task

        Args:
            task_name (str): task的名字(处理的视频或者视频源的名字) Example：lot_15.mp4

        Returns:
            Boolen:存在返回True否则返回False
        """
        if task_name in self.tasks.keys():
            try:
                self.tasks[task_name].kill()
                # 等待2秒，让task进程都停止都再回收内存,以防止task停止信号量过早被gc回收
                time.sleep(1)
            except RuntimeError as e:
                raise e
            finally:
                # 回收task
                del self.tasks[task_name]
                self.info_pool.remove(task_name)
        else:
            raise RuntimeError('TaskManger中不存在名字为{}的task'.format(task_name))

    def resume(self, task_name):
        """使指定的task从挂起状态恢复

        Args:
            task_name (str): task的名字(处理的视频或者视频源的名字) Example：lot_15.mp4

        Returns:
            Boolen:存在返回True否则返回False
        """
        if task_name in self.tasks.keys():
            # 检查当前是否已经有task在运行
            for task in self.tasks.values():
                if task.is_running():
                    raise RuntimeError('已经有Task在运行状态中，无法启动该Task')
            task = self.tasks[task_name]
            task.start()
            Thread(target=read_info_from_task, args=(task.get_readqs(), task_name, self.info_pool,)).start()
        else:
            raise RuntimeError('TaskManger中不存在名字为{}的task'.format(task_name))

    def get_progress_info(self,task_name: str):
        return self.info_pool.get_progress_info(task_name)

    def get_analysis_info(self,task_name: str):
        return self.info_pool.get_analysis_info(task_name)
    
    def get_pass_count_table(self,task_name: str):
        return self.info_pool.get_pass_count_table(task_name)