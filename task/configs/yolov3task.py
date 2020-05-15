import torch

Yolov3TaskCfg = {
    'head': [
        {
            'type': 'VideoFileHead',
            'filename': './test.mp4',
            'step': 8,
            'cache_capacity': 100
        }
    ],
    'detector': [
        {
            'type': 'Yolov3Detector',
            'device': torch.device('cuda' if torch.cuda.is_available() else 'cpu'),
            'batch_size': 8
        }
    ],

    'backbones': [
        [
            {
                'type': 'DrawBoundingBoxComponent'  # 画框框
            },
            {
                'type': 'FpsCollectorComponent',
                'isPrint': True
            },
            {
                'type': 'WriteVideoComponent',
                'resolution': (1920, 1080),
                'fps': 30
            }
        ]
    ]
}
