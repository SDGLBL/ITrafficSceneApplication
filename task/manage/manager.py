import os
from os.path import exists,join
from ..build import TaskBuilder
from multiprocessing import Pool
from cfg import TaskConfig
import importlib

class TaskManager(object):
    def __init__(self):
        super().__init__()
        # self.tasks:[
        #   { 
        #   'task_name':task名字 Example:lot_15.mp4
        #   'task_snapshot_url':task处理的视频的截图 Example:/static/data/video/lot_15.jpg
        #   'task_progress':task处理的进度,范围为[0-100] Example:20
        #   'task_mqs':[task2main_queue]
        #   }
        # ...]
        self.tasks = []
    
    def submit(self,*args, **kwargs):
        # 如果超过了最多的提交数量限制，则返回 False
        if len(self.tasks) >= TaskConfig.MAX_TASK_NUM:
            return False
        task_type = kwargs['task_type']
        # 通过字符串导入Task的Config字典
        task_config = importlib.import_module('task.configs.'+task_type).TaskConfig
        for task_component_cfg in kwargs['task_component_cfgs']:
            # TODO: 此处需要完成task的必要信息注入过程
            pass
        pass

    def is_exist(self,task_name:str):
        """检查指定的task是否已经存在

        Args:
            task_name (str): task的名字(处理的视频或者视频源的名字) Example：lot_15.mp4
        Returns:
            Boolen:存在返回True否则返回False
        """        
        if task_name in [task['task_name'] for task in self.tasks]:
            return True
        else:
            return False