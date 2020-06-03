from easydict import EasyDict
import os.path as osp
Cfg = EasyDict()

# 数据库信息
Cfg.host='localhost'
Cfg.user='root'
Cfg.password='591343671'
Cfg.database='world'
Cfg.port=3306
Cfg.charset='utf8'
# Redis配置
Cfg.redis_host='localhost'
Cfg.redis_port = 6379 #redis运行的端口号
Cfg.redis_decode_responses= True #将字节转换为字符
Cfg.redis_database=0

# 程序组件运行配置
Cfg.batch_size=2 # head一次读取多少张图片，必须为2的倍数或者为1
Cfg.is_print_fps=True # 是否显示处理的fps速度
Cfg.allow_stop_time=2 # 禁止停车区域允许停车的最长时间，单位为秒
Cfg.img_save_dir='criminal'
Cfg.video_save_dir=osp.join("videoData","video")
Cfg.emd_save_dir=''
Cfg.frame_image_save_dir=osp.join("videofrontend","static","frameimages")
Cfg.snapshot_path=osp.join("videofrontend","static","snapshotimages")
#选择 task的configs
Cfg.task_selected="crossRoadsTask"