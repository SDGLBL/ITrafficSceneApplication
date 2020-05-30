import multiprocessing as mp
import platform
from queue import Empty
from threading import Thread

import mmcv
import numpy as np
import argparse

from task.build import TaskBuilder
from task.configs.modellingTask import ModellingTaskCfg

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-vf',type=str,default='videoData/video/lot_15.mp4',help='作为建模素材视频的地址')
    parser.add_argument('-out',type=str,default='videoData/model/lot_15_2.emd',help='模型保存位置，请命名为xxx.emd格式')
    parser.add_argument('--revise', action = 'store_true', help = '选择表示对模型实行方向矫正，对拍摄视角较正的视频不建议开启')
    parser.add_argument('-n',type=int,default=50000,help='提取的数据量，默认为50000')
    return parser.parse_args()

def read_info_from_task(mqs):
    try:
        while True:
            for mq in mqs:
                img_info = mq.get(timeout=5)
    except Empty:
        print('主进程结束')

if __name__ == '__main__':
    # Linux平台启动
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)
    # 建模任务
    args = parse_args()
    print(args.vf)
    print(args.out)
    print(args.revise)
    ModellingTaskCfg['head'][0]['filename'] = args.vf
    ModellingTaskCfg['backbones'][0][1]['modelPath'] = args.out
    ModellingTaskCfg['backbones'][0][1]['revise'] = args.revise
    ModellingTaskCfg['backbones'][0][1]['dataNum'] = args.n
    task = TaskBuilder(ModellingTaskCfg)
    mqs = task.build()
    task.start()
    readt = Thread(target=read_info_from_task, args=(mqs,))
    readt.start()
    readt.join()