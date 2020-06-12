import argparse
import multiprocessing as mp
import os.path as osp
import platform
from queue import Empty
from threading import Thread

from task.configs.modelling.modellingTask import TaskCfg
from task.task import Task


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, default='videoData/video/lot_15.mp4', help='作为建模素材视频的地址')
    parser.add_argument('-o', type=str, default='videoData/model/lot_15_2.emd', help='模型保存位置，请命名为xxx.emd格式')
    parser.add_argument('--revise', action='store_true', help='选择表示对模型实行方向矫正，对拍摄视角较正的视频不建议开启')
    parser.add_argument('-n', type=int, default=50000, help='提取的数据量，默认为50000')
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
    if not osp.exists(args.i):
        raise AttributeError('输入文件不存在')
    print('处理视频为{},保存环境模型到{},是否开启方向矫正：{}'.format(args.i, args.o, args.revise))
    TaskCfg['head'][0]['filename'] = args.i
    TaskCfg['backbones'][0][1]['modelPath'] = args.o
    TaskCfg['backbones'][0][1]['revise'] = args.revise
    TaskCfg['backbones'][0][1]['dataNum'] = args.n
    task = Task(TaskCfg)
    mqs = task.build()
    task.start()
    readt = Thread(target=read_info_from_task, args=(mqs,))
    readt.start()
    readt.join()
