from easydict import EasyDict
import os.path as osp
Cfg = EasyDict()

# 程序组件运行配置
Cfg.batch_size=8 # head一次读取多少张图片，必须为2的倍数或者为1
Cfg.is_print_fps=True # 是否显示处理的fps速度
Cfg.allow_stop_time=2 # 禁止停车区域允许停车的最长时间，单位为秒
Cfg.img_save_dir='criminal'