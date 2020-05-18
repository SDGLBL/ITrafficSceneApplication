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
                
                'type': 'FpsCollectorComponent',
                'isPrint': True
                # 'type': 'infoPort'
                #'type': 'stateAnalysis',
                #'eModelPath': 'components/backbones/environmentModeling/eModeldata/lot_15.emd'
                #'type':'saveImgInfo'
            }
        ]
    ]
}
