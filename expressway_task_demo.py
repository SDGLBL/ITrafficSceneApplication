from os.path import join
import multiprocessing as mp
import numpy as np
import platform
from cfg import DataConfig, TaskConfig
from task import TaskManager, ImgInfoPool, get_cfgDataHandler
import importlib

if __name__ == '__main__':
    # Linux平台启动
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)
    img_info_pool = ImgInfoPool(max_size=30)
    tm = TaskManager(img_info_pool)
    cfg_data = {
        "task_type":"expresswayTaskFake",
        "filename": "gs.mp4", 
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
    tm.submit(task_name='gs.mp4', task_cfg=task_cfg)
    tm.resume(task_name='gs.mp4')
    