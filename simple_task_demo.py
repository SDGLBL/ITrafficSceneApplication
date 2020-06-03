import multiprocessing as mp
import platform
from queue import Empty
from threading import Thread

import mmcv
import numpy as np

from task.build import TaskBuilder
from task.configs.crossRoadsTaskFake import CrossRoadsTaskFakeCfg
from task.configs.simpleTaskFake import SimpleTaskFakeCfg


def read_info_from_task(mqs):
    try:
        while True:
            for mq in mqs:
                img_info = mq.get(timeout=5)
                if len(img_info['analysis']) > 0:
                    print(img_info['analysis'])
    except Empty:
        print('主进程结束')

if __name__ == '__main__':
    # Linux平台启动
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)
    parking_monitoring_area = np.ones((1080, 1920), dtype=int)
    parking_monitoring_area[400:800, 750:1250] = 0
    lane_monitoring_area = np.ones((1080, 1920), dtype=int)
    lane_monitoring_area[400:800, 750:1250] = 2
    # 如下是一个路口演示demo
    # 因为使用FakeCfg模拟目标探测的效果所以需要在head导入视频路径和已经探测好的json文件
    for name,component_cfg in SimpleTaskFakeCfg.items():
        if name == 'head':
            component_cfg[0]['filename'] = 'videoData/video/lot_15.mp4'
            component_cfg[0]['json_filename'] = 'videoData/json/lot_15.json'
        elif name == 'tracker':
            continue
        elif name == 'backbones':
            for backbone in component_cfg:
                for backbone_component_cfg in backbone:
                    print(backbone_component_cfg)
                    cfg_type = backbone_component_cfg['type']
                    if cfg_type == 'PathExtract':
                        backbone_component_cfg['eModelPath'] = 'videoData/model/lot_15.emd'
                    elif cfg_type == 'TrafficStatistics':
                        backbone_component_cfg['eModelPath'] = 'videoData/model/lot_15.emd'
                        backbone_component_cfg['is_process'] = True # 车流统计模块需要选择是否开启
                    elif cfg_type == 'ParkingMonitoringComponent':
                        backbone_component_cfg['monitoring_area'] = parking_monitoring_area
                        backbone_component_cfg['is_process'] = False
                    elif cfg_type == 'LaneMonitoringComponent':
                        backbone_component_cfg['monitoring_area'] = lane_monitoring_area
                        backbone_component_cfg['no_allow_car'] = {2:['car']}
                        backbone_component_cfg['is_process'] = False
    task = TaskBuilder(CrossRoadsTaskFakeCfg)
    mqs = task.build()
    task.start()
    readt = Thread(target=read_info_from_task, args=(mqs,))
    readt.start()
    readt.join()
