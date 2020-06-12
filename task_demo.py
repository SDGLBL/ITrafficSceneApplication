from os.path import join

import numpy as np

from cfg import DataConfig
from task import TaskManager

if __name__ == "__main__":
    tm = TaskManager()
    parking_monitoring_area = np.ones((1080, 1920), dtype=int)
    parking_monitoring_area[400:800, 750:1250] = 0
    lane_monitoring_area = np.ones((1080, 1920), dtype=int)
    lane_monitoring_area[400:800, 750:1250] = 2
    cfg = {
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
    tm.submit(task_name='lot_15.mp4', task_type='crossRoadsTaskFake', task_cfgs=cfg)
    # time.sleep(5)
    # tm.suspend('lot_15.mp4')
    # print('lot_15.mp4挂起')
    # time.sleep(5)
    # tm.resume('lot_15.mp4')
    # print('恢复运行')
    # time.sleep(5)
    # tm.kill('lot_15.mp4')
