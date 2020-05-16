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
    'tracker': [
        {
            'type': 'DeepSortTracker'
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
            },
            {
                # 推流组件,本地测试用localhost,服务器测试记得更换localhost
                'type': 'RtmpWriteComponent',
                'resolution': (1920, 1080),
                'fps': 30,
                'rtmpUrl': 'rtmp://localhost:1935/live/home'
            }
        ]
    ]
}
