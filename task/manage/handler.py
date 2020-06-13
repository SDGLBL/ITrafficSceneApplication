import os
import cv2
import numpy as np
from os.path import exists,join
from cfg import TaskConfig
import importlib

class BaseTaskCfgDataHandler(object):
    def __init__(self):
        pass


    def handle(self,task_cfg_data: dict):
        """处理自定义的task数据并注入到TaskCfg中
        :param task_cfg_data: 自定义的task参数字典
        :return: 完成数据注入后的TaskCfg
        """
        if 'task_type' not in task_cfg_data.keys():
            raise RuntimeError('task_cfg_data必须标明其task_type')
        raise RuntimeError("无法处理{}参数字典".format(task_cfg_data['task_type']))
        return None


class TaskCfgDataHandler(BaseTaskCfgDataHandler):
    """crossRoadsTaskFake的TaskCfg注入数据处理类
    """    
    def __init__(self):
        super().__init__()
        self.config_dir = TaskConfig.SCENE_CFG_DIR
        self.support_tasks = ['crossRoadsTask', 'crossRoadsTaskFake']

    def handle(self, task_cfg_data: dict):
        """提交一个Task
        Args:
            task_cfg_data: task的数据注入字典，格式为一个字典，格式请看Example
        Returns:
            返回是否返回值
        Examples:
            >>> tm = TaskManager()
            >>> parking_monitoring_area = np.ones((1080, 1920), dtype=int)
            >>> parking_monitoring_area[400:800, 750:1250] = 0
            >>> lane_monitoring_area = np.ones((1080, 1920), dtype=int)
            >>> lane_monitoring_area[400:800, 750:1250] = 2
            >>> cfg = {
            >>> 'task_type':'crossRoadsTaskFake',
            >>> 'head':{
            >>>    'filename':join(DataConfig.VIDEO_DIR,'lot_15.mp4'),
            >>>    'json_filename':join(DataConfig.JSON_DIR,'lot_15.json')
            >>> },
            >>> 'backbones':[
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
            >>> ]
            >>> }
            >>> tm.submit(task_name='lot_15.mp4',**{
            >>>    'task_type':'crossRoadsTaskFake',
            >>>    'task_component_cfgs':cfg
            >>> })
            >>> tm.kill('lot_15.mp4')
        """      
        if 'task_type' not in task_cfg_data.keys():
            raise RuntimeError('task_cfg_data必须标明其task_type')
        if task_cfg_data['task_type'] not in self.support_tasks:
            super().handle(task_cfg_data)
        task_type = task_cfg_data['task_type']
        del task_cfg_data['task_type']
        # 通过给定的路径导入Task的Config字典
        task_config_py_path = (self.config_dir + task_type).replace('.', os.sep) + '.py'
        if not exists(task_config_py_path):
            raise RuntimeError('无法导入{}，因为该文件不存在'.format(task_config_py_path))
        task_config = importlib.import_module(self.config_dir + task_type).TaskCfg
        # ----------------------------------
        # 开始注入Task运行必须参数
        # ----------------------------------
        for task_component_type, components_cfg in task_cfg_data.items():
            # 处理非backbone组件的cfg,根据传递进来的key,value注入参数
            if task_component_type != 'backbones':
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
        return task_config





