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
                'type': 'PathExtract'
            },
            {
                'type': 'Modelling'
            }
        ]
    ]
}
