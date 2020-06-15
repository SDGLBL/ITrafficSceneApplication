from os.path import join

import numpy as np

from cfg import DataConfig, TaskConfig
from task import TaskManager
import importlib

if __name__ == '__main__':
    tm = TaskManager(config_dir=TaskConfig.SIMPLE_CFG_DIR)
    cfg_data = {
        "task_type":"crossRoadsTaskFake",
        "filename": "lot_15.mp4", 
        "parking_monitoring_area": [
            [[1250, 800], [1250, 400], [750, 400], [750, 800]]
            ], 
        "lane_monitoring_area": [
            [[1250, 800], [1250, 400], [750, 400], [750, 800]]
            ], 
        "lane_no_allow_cars": {"2": ["car"]}
        }
    task_type = cfg_data['task_type']
    get_cfg = importlib.import_module(TaskConfig.SCENE_CFG_DIR + task_type).get_injected_cfg
    task_cfg = get_cfg(cfg_data)
    tm.submit(task_name='lot_15.mp4', task_cfgs=task_cfg)
