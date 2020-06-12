from os.path import join


class TaskConfig:
    BATCH_SIZE = 8  # head一次读取多少张图片，必须为2的倍数或者为1
    IS_PRINT_FPS = True  # 是否显示处理的fps速度
    ALLOW_STOP_TIME = 2  # 禁止停车区域允许停车的最长时间，单位为秒
    RTMP_URL = 'rtmp://localhost:1935/live/home'  # 默认视频流地址
    CRIMINAL_DIR = 'static/data/criminal'  # 违规拍照保存目录
    MAX_TASK_NUM = 10  # Task队列长度
    SCENE_CFG_DIR = 'task.configs.scene.'  # 交通场景task config目录，用于动态导入taskcfg字典
    MODELLING_CFG_DIR = 'task.configs.modelling.'  # 交通场景建模task config目录，用于动态导入taskcfg字典
    SIMPLE_CFG_DIR = 'task.configs.simple.'  # 简单演示task config目录，用于动态导入taskcfg字典


class DataConfig:
    DATA_DIR = 'static/data'  # Task静态数据目录
    VIDEO_DIR = join(DATA_DIR, 'video')  # 视频保存目录
    EMODEL_DIR = join(DATA_DIR, 'emodel')  # 环境模型保存目录
    JSON_DIR = join(DATA_DIR, 'json')  # FakeTask需要的json保存的目录
    SNAPSHOT_DIR = join(DATA_DIR, 'snapshot')  # 视频快照存储目录
    VIDEO_TYPE = ['mp4', 'avi']  # 可以处理的视频格式
