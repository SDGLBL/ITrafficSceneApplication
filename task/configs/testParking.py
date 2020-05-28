from cfg import Cfg
TestParkingTaskCfg = {
    'head': [
         {
            'type': 'EquivalentHead',
            'filename': './lot_15.mp4',
            'json_filename': './img_info.json',
            'step': Cfg.batch_size,
            'cache_capacity': 100
        }
    ],
    'backbones': [
        [

            # fps计数组件
            {
                'type': 'FpsCollectorComponent',
                'isPrint': Cfg.is_print_fps
            },
            {
                'type': 'ParkingMonitoringComponent',
                'monitoring_area': None,
                'allow_stop_time': Cfg.allow_stop_time
            },
            # 数据库写入组件
            {
                'type': 'InformationCollectorComponent',
                'host': Cfg.host,
                'user': Cfg.user,
                'password': Cfg.password,
                'db': Cfg.database,
                'img_save_path':Cfg.img_save_dir
            }
        ]
    ]
}
