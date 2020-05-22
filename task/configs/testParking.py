TestParkingTaskCfg = {
    'head': [
        {
            'type': 'EquivalentHead',
            'filename': './lot_15.mp4',
            'json_filename': './img_info.json',
            'step': 8,
            'cache_capacity': 100
        }
    ],
    'backbones': [
        [

            # fps计数组件
            {
                'type': 'FpsCollectorComponent',
                'isPrint': True
            },
            {
                'type': 'ParkingMonitoringComponent',
                'monitoring_area': None,
                'allow_stop_time': 20
            },
            # 数据库写入组件
            {
                'type': 'InformationCollectorComponent',
                'host': 'localhost',
                'user': 'lijie',
                'password': '8241660925',
                'db': 'itsa'
            }
        ]
    ]
}
