from os.path import join
import os
import multiprocessing as mp
import numpy as np
import argparse
import platform
from utils.sqlitedao import create_database
from cfg import DataConfig, TaskConfig
from task import TaskManager, ImgInfoPool, get_cfgDataHandler
import importlib

def args_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',type=str,help='input video')
    return parser.parse_args()

if __name__ == "__main__":
    # Linux平台启动
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)
    img_info_pool = ImgInfoPool(max_size=30)
    tm = TaskManager(img_info_pool)
    args = args_parse()
    cfg_data = {
        "task_type":"modellingTask",
        "filepath": args.i,
        }
    task_type = cfg_data['task_type']
    get_cfg = importlib.import_module(TaskConfig.MODELLING_CFG_DIR + task_type).get_injected_cfg
    task_cfg = get_cfg(cfg_data)
    tm.submit(task_name=os.path.basename(args.i), task_cfg=task_cfg)
    tm.resume(task_name=os.path.basename(args.i),is_join=True)