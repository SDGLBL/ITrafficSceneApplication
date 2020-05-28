from cfg import Cfg
CrossRoadsTaskFakeCfg = {
    'head': [
        {
            'type': 'EquivalentHead',
            'filename': 'videoData/video/gta5_small.mp4',
            'json_filename': 'videoData/json/gta5_small.json',
            'step': Cfg.batch_size,
            'cache_capacity': 100,
            'haveImg': True
        }
    ],
    'tracker': [
        {
            'type': 'SORT_Track'
        }
    ],
    'backbones': [
        [
            {
                'type': 'PathExtract',   # 路径分析模块，基础模块，不可或缺
                'eModelPath': 'videoData/model/gta5_small.emd'
            },
            {
                'type': 'TrafficStatistics',     # 车流统计模块
                'eModelPath': 'videoData/model/gta5_small.emd'
            },
            {
                'type': 'SaveImgInfo',
                'savePath': 'videoData/json/gta5_small_end.json'
            }
        ]
    ]
}
