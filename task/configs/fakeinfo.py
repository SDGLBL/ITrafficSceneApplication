FakedTaskCfg = {
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

            {
                'type': 'DrawBoundingBoxComponent'  # 画框框
            },
            # fps计数组件
            {
                'type': 'FpsCollectorComponent',
                'isPrint': True
            },
            # 写视频流
            {
                'type': 'WriteVideoComponent',
                'resolution': (1920, 1080),
                'fps': 30
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
