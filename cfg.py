from easydict import EasyDict
Cfg = EasyDict()

# 数据库信息
Cfg.host='localhost'
Cfg.user='lijie'
Cfg.password=''
Cfg.database='itsa'

# 程序组件运行信息
Cfg.batch_size=8 # head一次读取多少张图片，必须为2的倍数或者为1
Cfg.is_print_fps=True # 是否显示处理的fps速度
Cfg.allow_stop_time=20 # 禁止停车区域允许停车的最长时间，单位为秒
