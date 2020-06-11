TaskCfg = {
    'task_name':'环境建模Fake',
    'head': 
        {
            'type': 'EquivalentHead',
            'filename': None,
            'json_filename': None,
            'step': 8,
            'cache_capacity': 100,
            'haveImg': False
        }
    ,
    'backbones': [
        [
            {
                'type': 'PathExtract'   # 路径分析模块，基础模块，不可或缺
            },
            {
                'type': 'Modelling',
                'mapSize':(1080,1920),
                'modelPath': None 
            }
        ]
    ]
}
