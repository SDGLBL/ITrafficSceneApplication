
from os.path import exists,join
from os import mkdir

class TaskConfig:
    BATCH_SIZE = 8 # head一次读取多少张图片，必须为2的倍数或者为1
    IS_PRINT_FPS = True # 是否显示处理的fps速度
    ALLOW_STOP_TIME = 2 # 禁止停车区域允许停车的最长时间，单位为秒
    RTMP_URL = 'rtmp://localhost:1935/live/home' # 默认视频流地址



class DataConfig:
    DATA_DIR = 'data'
    VIDEO_DIR = join(DATA_DIR,'video')
    EMODEL_DIR = join(DATA_DIR,'emodel')
    JSON_DIR = join(DATA_DIR,'json')
    CRIMINAL_DIR = join(DATA_DIR,'criminal')