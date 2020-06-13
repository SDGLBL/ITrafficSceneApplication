from os.path import join

import numpy as np

from cfg import DataConfig
from task import TaskManager
from task.manage.infopool import ImgInfoPool
from threading import Thread
import time
def read_info_from_pool(task_name,pool:ImgInfoPool):
    while True:
        try:
            x = pool.get(task_name)
            if x is not None:
                print('从信息池中读取到的信息为')
                print(x)
            time.sleep(10)
        except:
            pass


if __name__ == "__main__":
    pool = ImgInfoPool(60)
    tm = TaskManager(pool)
    parking_monitoring_area = np.ones((1080, 1920), dtype=int)
    parking_monitoring_area[400:800, 750:1250] = 0
    lane_monitoring_area = np.ones((1080, 1920), dtype=int)
    lane_monitoring_area[400:800, 750:1250] = 2
    cfg = {
        'task_type':'crossRoadsTaskFake',
        'head': {
            'filename': join(DataConfig.VIDEO_DIR, 'lot_15.mp4'),
            'json_filename': join(DataConfig.JSON_DIR, 'lot_15.json')
        },
        'backbones': [
            {
                'type': 'PathExtract',
                'eModelPath': join(DataConfig.EMODEL_DIR, 'lot_15.emd')
            },
            {
                'type': 'TrafficStatistics',
                'eModelPath': join(DataConfig.EMODEL_DIR, 'lot_15.emd'),
                'is_process': True
            },
            {
                'type': 'ParkingMonitoringComponent',  # 违章停车监控组件
                'monitoring_area': parking_monitoring_area,  # 监控区域，必须赋值
                'is_process': True  # 是否开启该组件
            },
            {
                'type': 'LaneMonitoringComponent',  # 违法占用车道组件
                'monitoring_area': lane_monitoring_area,  # 监控区域，必须赋值
                'no_allow_car': {2: ['car']},  # 比如{1:['car','truck']} 则在monitoring_area中值为1的区域内不允许出现car和truck
                'is_process': True  # 是否开启该组件
            }
        ]
    }
    from task import get_cfgDataHandler
    handler = get_cfgDataHandler()
    cfg = handler.handle(cfg)
    tm.submit(task_name='lot_15.mp4', task_cfg=cfg)
    tm.resume('lot_15.mp4')
    t = Thread(target=read_info_from_pool,args=('lot_15.mp4',pool,))
    t.start()
    # time.sleep(10)
    # print('挂起')
    # tm.suspend('lot_15.mp4')
    # time.sleep(10)
    # print('唤醒')
    # tm.resume('lot_15.mp4')
    # time.sleep(10)
    # print('杀死')
    # tm.kill('lot_15.mp4')
