import importlib
import os
from os.path import exists
from os.path import join
from queue import Empty

import numpy as np
from threading import Thread
from cfg import TaskConfig, DataConfig
from task.task import Task
from utils.logger import get_logger


def read_info_from_task(mqs):
    try:
        while True:
            for mq in mqs:
                img_info = mq.get(timeout=20)
                if len(img_info['analysis']) > 0:
                    print(img_info['analysis'])
    except Empty:
        print('主进程结束')
        return


class TaskManager(object):
    def __init__(self, config_dir=TaskConfig.SCENE_CFG_DIR):
        super().__init__()
        # self.tasks:[
        #   { 
        #   'task_name':task名字 Example:lot_15.mp4
        #   'task_snapshot_url':task处理的视频的截图 Example:/static/data/video/lot_15.jpg
        #   'task_progress':task处理的进度,范围为[0-100] Example:20
        #   'task_mqs':[task2main_queue]
        #   }
        # ...]
        self.config_dir = config_dir
        self.tasks = {}
        self.logger = get_logger('logs/task.log')

    def submit(self, task_name: str, task_type: str, task_cfgs: dict):
        """提交一个Task
        Args:
            task_name: task的名字，需要保证不重复，其会作为task的唯一标识符，建议传入视频或摄像头名称
            task_type: task的类型，其值应该为task.configs下config的py文件名，用于动态导入TaskCfg
            task_cfgs: task的数据注入字典，格式为一个字典，格式请看Example
        Returns:
            返回是否返回值
        Examples:
            >>> tm = TaskManager()
            >>> parking_monitoring_area = np.ones((1080, 1920), dtype=int)
            >>> parking_monitoring_area[400:800, 750:1250] = 0
            >>> lane_monitoring_area = np.ones((1080, 1920), dtype=int)
            >>> lane_monitoring_area[400:800, 750:1250] = 2
            >>> cfg = {
            >>>'head':{
            >>>    'filename':join(DataConfig.VIDEO_DIR,'lot_15.mp4'),
            >>>    'json_filename':join(DataConfig.JSON_DIR,'lot_15.json')
            >>>},
            >>>'backbones':[
            >>>    {
            >>>        'type':'PathExtract',
            >>>        'eModelPath':join(DataConfig.EMODEL_DIR,'lot_15.emd')
            >>>    },
            >>>    {
            >>>        'type':'TrafficStatistics',
            >>>        'eModelPath':join(DataConfig.EMODEL_DIR,'lot_15.emd'),
            >>>        'is_process':True
            >>>    },
            >>>    {
            >>>        'type': 'ParkingMonitoringComponent', # 违章停车监控组件
            >>>        'monitoring_area': parking_monitoring_area, # 监控区域，必须赋值
            >>>        'is_process':True # 是否开启该组件
            >>>    },
            >>>    {
            >>>        'type': 'LaneMonitoringComponent', # 违法占用车道组件
            >>>        'monitoring_area':lane_monitoring_area,  # 监控区域，必须赋值
            >>>        'no_allow_car':{2:['car']}, # 比如{1:['car','truck']} 则在monitoring_area中值为1的区域内不允许出现car和truck
            >>>        'is_process':True # 是否开启该组件
            >>>    }
            >>>]
            >>>}
            >>>tm.submit(task_name='lot_15.mp4',**{
            >>>    'task_type':'crossRoadsTaskFake',
            >>>    'task_component_cfgs':cfg
            >>>})
            >>> tm.kill('lot_15.mp4')
        """
        # 如果超过了最多的提交数量限制，则返回 False
        if len(self.tasks) >= TaskConfig.MAX_TASK_NUM:
            return False
        # 通过给定的路径导入Task的Config字典
        task_config_py_path = (self.config_dir + task_type).replace('.', os.sep) + '.py'
        if not exists(task_config_py_path):
            raise RuntimeError('无法导入{}，因为该文件不存在'.format(task_config_py_path))
        task_config = importlib.import_module(self.config_dir + task_type).TaskCfg
        # ----------------------------------
        # 开始注入Task运行必须参数
        # ----------------------------------
        for task_component_type, components_cfg in task_cfgs.items():
            # TODO: 此处需要完成task的必要信息注入过程
            # 首先确定该task的名字
            if task_component_type == 'task_name':
                self.logger.info('提交了一个{} Task'.format(components_cfg))
            # 然后处理非backbone组件的cfg,根据传递进来的key,value注入参数
            elif task_component_type != 'backbones':
                for key, value in components_cfg.items():
                    # 检查组件中是否存在该需要赋值的对象
                    check = task_config[task_component_type]
                    if key not in check.keys() or (check[key] is not None and check[key] is not False):
                        raise RuntimeError(
                            '{}任务的{}组件不需要对其{}参数进行赋值,因为此参数不存在或者不需要赋值'.format(task_type, task_component_type, key))
                    # 检查完毕开始注入参数
                    task_config[task_component_type][key] = value
            # 处理backbones的参数注入，由于backbones是二维数组，需要进行多个循环
            elif task_component_type == 'backbones':
                # 首先将需要注入的数据先取出来
                for backbone_comp_cfg_inject in components_cfg:
                    # 获取需要注入的组件的type
                    backbone_comp_type = backbone_comp_cfg_inject['type']
                    del backbone_comp_cfg_inject['type']
                    # 遍历task_config中所有的backbone组件，并注入参数
                    for backbone_index, backbone_cfg in enumerate(task_config[task_component_type]):
                        for backbone_comp_index, backbone_comp_cfg in enumerate(backbone_cfg):
                            # 检查组件中是否存在该需要赋值的对象
                            check = task_config[task_component_type][backbone_index][backbone_comp_index]
                            # 如果不是需要注入的组件直接跳过
                            if backbone_comp_type != check['type']:
                                continue
                            # 确定该组件需要注入数据，则遍历注入数据，将数据注入组件中
                            for key, value in backbone_comp_cfg_inject.items():
                                if key not in check.keys() or (check[key] is not None and check[key] is not False):
                                    raise RuntimeError(
                                        '{}任务的{}组件不需要对其{}参数进行赋值,因为此参数不存在或者不需要赋值'.format(task_type, backbone_comp_type,
                                                                                        key))
                                task_config[task_component_type][backbone_index][backbone_comp_index][key] = value
        # ----------------------------------
        # 完成注入开始生成Task
        # ----------------------------------
        task = Task(task_config)
        mqs = task.build()
        task.start()
        # 启动读取数据线程
        Thread(target=read_info_from_task, args=(mqs,)).start()
        self.tasks[task_name] = task

        return

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
            return True
        else:
            return False

    def kill(self, task_name):
        """直接杀死指定的task

        Args:
            task_name (str): task的名字(处理的视频或者视频源的名字) Example：lot_15.mp4

        Returns:
            Boolen:存在返回True否则返回False
        """
        if task_name in self.tasks.keys():
            self.tasks[task_name].kill()
            return True
        else:
            return False

    def resume(self, task_name):
        """使指定的task从挂起状态恢复

        Args:
            task_name (str): task的名字(处理的视频或者视频源的名字) Example：lot_15.mp4

        Returns:
            Boolen:存在返回True否则返回False
        """
        if task_name in self.tasks.keys():
            self.tasks[task_name].start()
            return True
        else:
            return False
