import torch
PreheatTaskCfg = {
    'head': [
        {
            'type': 'VideoFileHead',
            'filename': './lot_15.mp4',
            'step': 8,
            'cache_capacity': 100
        }
    ],
    'detector': [
        {
            'type': 'Yolov4Detector',
            'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
            'batch_size': 8
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
                # 'type': 'infoPort'
                'type': 'stateAnalysis',
                'eModelPath': 'components/backbones/environmentModeling/eModeldata/lot_15.emd'
            }
        ]
    ]
}
