from cfg import Cfg
SimpleTaskFakeCfg = {
    'head': [
        {
            'type': 'EquivalentHead',
            'filename': 'videoData/video/lot_15.mp4',
            'json_filename': 'videoData/json/lot_15.json',
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
            # fps计数组件
            {
                'type': 'FpsCollectorComponent',
                'isPrint': Cfg.is_print_fps
            },
            {
                'type': 'PathExtract',   # 路径分析模块，基础模块，不可或缺
                'eModelPath':'videoData/model/lot_15.emd' #视频环境模型路径，必须赋值
            },
            {
                'type': 'TrafficStatistics',     # 车流统计模块
                'eModelPath': 'videoData/model/lot_15.emd', #视频环境模型路径，必须赋值
                'is_process':True # 是否开启该组件
            },
            {
                'type': 'ParkingMonitoringComponent', # 违章停车监控组件
                'monitoring_area': None, # 监控区域，必须赋值
                'allow_stop_time': Cfg.allow_stop_time,
                'is_process':False # 是否开启该组件
            },
            {
                'type': 'LaneMonitoringComponent', # 违法占用车道组件
                'monitoring_area':None,  # 监控区域，必须赋值
                'no_allow_car':{}, # 比如{1:['car','truck']} 则在monitoring_area中值为1的区域内不允许出现car和truck
                'is_process':False # 是否开启该组件
            },
            {
                'type': 'DrawBoundingBoxComponent'  # 画框框
            },
            {
                'type': 'DrawInfoComponent'     # 绘制信息板
            }
        ]
    ]
}