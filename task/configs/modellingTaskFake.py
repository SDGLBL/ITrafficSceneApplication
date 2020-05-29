ModellingTaskFakeCfg = {
    'head': [
        {
            'type': 'EquivalentHead',
            'filename': 'videoData/video/gta5_small.mp4',
            'json_filename': 'videoData/json/gta5_small.json',
            'step': 8,
            'cache_capacity': 100,
            'haveImg': False
        }
    ],
    'backbones': [
        [
            {
                'type': 'PathExtract'   # 路径分析模块，基础模块，不可或缺
            },
            {
                'type': 'Modelling',
                'mapSize':(1080,1920),
                'modelPath': 'videoData/model/gta5_small.emd'
            }
        ]
    ]
}
