from task.manage.manager import TaskManager
from os.path import join
from cfg import DataConfig,TaskConfig
import numpy as np
import time
from task.configs.simple.simpleTaskFake import TaskCfg


if __name__ == '__main__':
    tm = TaskManager(config_dir=TaskConfig.SIMPLE_CFG_DIR)
    parking_monitoring_area = np.ones((1080, 1920), dtype=int)
    parking_monitoring_area[400:800, 750:1250] = 0
    lane_monitoring_area = np.ones((1080, 1920), dtype=int)
    lane_monitoring_area[400:800, 750:1250] = 2
    cfg = {
        'head':{
            'filename':join(DataConfig.VIDEO_DIR,'lot_15.mp4'),
            'json_filename':join(DataConfig.JSON_DIR,'lot_15.json')
        },
        'backbones':[
            {
                'type':'PathExtract',
                'eModelPath':join(DataConfig.EMODEL_DIR,'lot_15.emd')
            },
            {
                'type':'TrafficStatistics',
                'eModelPath':join(DataConfig.EMODEL_DIR,'lot_15.emd'),
                'is_process':True
            },
            {
                'type': 'ParkingMonitoringComponent', # 违章停车监控组件
                'monitoring_area': parking_monitoring_area, # 监控区域，必须赋值
                'is_process':True # 是否开启该组件
            },
            {
                'type': 'LaneMonitoringComponent', # 违法占用车道组件
                'monitoring_area':lane_monitoring_area,  # 监控区域，必须赋值
                'no_allow_car':{2:['car']}, # 比如{1:['car','truck']} 则在monitoring_area中值为1的区域内不允许出现car和truck
                'is_process':True # 是否开启该组件
            }
        ]
    }
    tm.submit(task_name='lot_15.mp4',**{
        'task_type':'simpleTaskFake',
        'task_component_cfgs':cfg
    })
