import importlib
import os
from copy import deepcopy
from functools import reduce
from os.path import exists, join

import cv2
import mmcv
import json
import numpy as np
from cfg import DataConfig, TaskConfig
from utils.logger import get_logger
from flask import Flask, jsonify, url_for, request
from task import TaskManager, ImgInfoPool, get_cfgDataHandler
from utils.sqlitedao import excute_sql, get_connection

app = Flask(__name__)


# ----------------------------------
# 获取各种列表
# url: /api/video/video_list 获取视频列表
# url: /api/task/task_list 获取task列表
# ----------------------------------
@app.route('/api/video/video_list')
def get_video_list():
    """获取视频列表以及对应的截图url

    Returns:
    Examples:
         >>> {
         >>>    "video_name" : 'lot_15.mp4',
         >>>    "video_snapshot" : '/static/data/video/lot_15.jpg'
         >>> }
    """
    # 获取文件夹中所有的视频名字
    video_names = [
        video_name for video_name in os.listdir(DataConfig.VIDEO_DIR)
        if video_name.split('.')[-1] in DataConfig.VIDEO_TYPE  # 此处进行差错检查，被处理的视频格式必须为指定可以处理的格式
    ]
    video_snapshot_paths = []
    for video_name in video_names:
        # 去掉视频文件后缀并拼接图像后缀
        video_snapshot_name = video_name.split('.')[0] + '.jpg'
        # 如果快照图像不存在则先进行创建
        video_path = join(DataConfig.VIDEO_DIR, video_name)
        video_snapshot_path = join(DataConfig.SNAPSHOT_DIR, video_snapshot_name)
        # 如果快照不存在,则自动创建快照
        if not exists(video_snapshot_path):
            cv2.imwrite(video_snapshot_path, mmcv.VideoReader(video_path)[0])
        video_snapshot_paths.append(video_snapshot_path)
    video_infos = [{
        'video_name': video_name,
        'video_snapshot_url': video_snapshot_path
    }
        for video_name, video_snapshot_path in zip(video_names, video_snapshot_paths)]
    server_loger.info('前端获取了视频列表{}'.format(video_infos))
    return jsonify(video_infos)


@app.route('/api/task/task_list')
def get_task_list():
    """获取后台Task列表

    Returns:
    Examples:
        >>> {
        >>>     'task_name': task名
        >>>     'task_snapshot_url': task处理的视频的截图
        >>>     'task_progress': taks进度
        >>> }
    """
    # TODO：此处应该配合manager的信息实时刷新，现在还未实现
    task_list = [
        task_name
        # {
        #     'task_name': task['task_name'],  # task名
        #     'task_snapshot_url': task['task_snapshot_url'],  # task处理的视频的截图
        #     'task_progress': task['task_progress'] # taks进度
        # }
        for task_name in task_manger.tasks.keys()
    ]
    server_loger.info('前端获取了task_list:{}'.format(task_list))
    return jsonify({'task_list': task_list})


@app.route('/api/task/task_cfg_list')
def get_task_cfg_list():
    """获取task_cfg_list,以得到支持的cfg和其名字
    Returns:
    Examples:
        >>>  [
        >>>     {
        >>>         "task_name": "路口场景Fake",
        >>>         "task_type": "crossRoadsTaskFake"
        >>>     },
        >>>     {
        >>>         "task_name": "路口场景",
        >>>         "task_type": "crossRoadsTask"
        >>>     }
        >>>]
    """
    task_cfg_list = []
    scene_cfg_dir = TaskConfig.SCENE_CFG_DIR.replace('.', os.sep)
    for name in os.listdir(scene_cfg_dir):
        if not os.path.isfile(join(scene_cfg_dir,name)):
            continue
        # 获取task的文件名,也就是其task_type
        task_type = name.split('.')[0]
        # 导入cfg获取其中文解释
        task_name = importlib.import_module(TaskConfig.SCENE_CFG_DIR + task_type).TaskCfg['task_name']
        task_cfg_list.append({
            'task_type': task_type,  # 比如 crossRoadsTask
            'task_name': task_name,  # 比如 路口场景
        })
    return jsonify(task_cfg_list)


# ------------------------
# 获取各种信息
# url: /api/video/video_info/<string:video_name> 获取视频video_name的信息情况，包括是否环境建模
#
# ----------------------

@app.route('/api/video/video_info/<string:video_name>')
def get_video_info(video_name: str):
    """获取指定视频的视频处理信息

    Args:
        video_name (str): 视频名字。比如：lot_15.mp4

    Returns:

    Examples:
         >>> {
         >>>    'is_exist_emd':True,
         >>>    'is_exist_json':False
         >>> }
    """
    video_info = {}
    video_name = video_name.split('.')[1]
    if not exists(join(DataConfig.EMODEL_DIR, video_name + '.emd')):
        video_info['is_exist_emd'] = True
    else:
        video_info['is_exist_emd'] = False
    if not exists(join(DataConfig.JSON_DIR, video_name + '.json')):
        video_info['is_exist_json'] = True
    else:
        video_info['is_exist_json'] = False
    server_loger.info('前端获取视频{}的信息{}'.format(video_name, video_info))
    return jsonify(video_info)


@app.route('/api/task/info/<string:task_name>')
def get_info_from_pool(task_name: str):
    try:
        info = img_info_pool.get(task_name)
        if info['info_type'] == 'illegal_parking':
            # 保存违规图像
            # for img in info['imgs']:
            pass
    except RuntimeError as e:
        # server_loger.error(e)
        return jsonify({'info': '获取失败，{}task还未存储信息'.format(task_name), 'is_success': False})


# -----------------------------
# 各种后台操作
# url: /api/video/del/<string:video_name> 删除video_name视频
# url: /api/task/submit/<string:task_name> 提交一个名字为task_name的task
# url: /api/task/suspend/<string:task_name> 挂起名字为task_name的task
# url: /api/task/kill/<string:task_name> 杀死名字为task_name的task
# url: /api/task/start/<string:task_name> 启动名字为task_name的task
# -----------------------------

@app.route('/api/video/del/<string:video_name>')
def delete_video(video_name: str):
    """删除指定的video

    Args:
        video_name (str): video的名字 。Example：lot_15.mp4
    """
    try:
        os.remove(join(DataConfig.VIDEO_DIR, video_name))
    except FileNotFoundError:
        server_loger.info('删除视频api被调用，指定被删除视频名字为{}，但其已经不存在了'.format(video_name))
        return jsonify({'info': '视频不存在', 'is_success': True})
    server_loger.info('删除了视频{}'.format(video_name))
    return jsonify({'info': '视频已经被移除', 'is_success': True})


@app.route('/api/task/submit/<string:task_name>', methods=['POST'])
def submit_task(task_name: str):
    """提交task
    :return:
    """
    # 先进行数据类型转换
    if request.method != 'POST':
        return jsonify({'info': '提交taskApi只接受POST'})
    # task_cfg_data = request.get_data()
    # task_cfg_data = json.loads(task_cfg_data)
    try:
        # 处理传递来的数据
        parking_monitoring_area = np.ones((1080, 1920), dtype=int)
        parking_monitoring_area[400:800, 750:1250] = 0
        lane_monitoring_area = np.ones((1080, 1920), dtype=int)
        lane_monitoring_area[400:800, 750:1250] = 2
        cfg = {
            'task_type': 'crossRoadsTaskFake',
            'head': {
                'filename': join(DataConfig.VIDEO_DIR, 'lot_15.mp4'),
                'json_filename': join(DataConfig.JSON_DIR, 'lot_15.json')
            },
            'backbones': [
                {
                    'type': 'PathExtract',
                    'eModelPath': join(DataConfig.EMODEL_DIR, 'lot_15.emd')
                },
                {
                    'type': 'TrafficStatistics',
                    'eModelPath': join(DataConfig.EMODEL_DIR, 'lot_15.emd'),
                    'is_process': True
                },
                {
                    'type': 'ParkingMonitoringComponent',  # 违章停车监控组件
                    'monitoring_area': parking_monitoring_area,  # 监控区域，必须赋值
                    'is_process': True  # 是否开启该组件
                },
                {
                    'type': 'LaneMonitoringComponent',  # 违法占用车道组件
                    'monitoring_area': lane_monitoring_area,  # 监控区域，必须赋值
                    'no_allow_car': {2: ['car']},  # 比如{1:['car','truck']} 则在monitoring_area中值为1的区域内不允许出现car和truck
                    'is_process': True  # 是否开启该组件
                }
            ]
        }
        task_cfg = cfg_data_handler.handle(cfg)
        # 提交任务到task manager
        task_manger.submit(task_name, task_cfg)
        server_loger.info('前端提交了task_name:{}任务'.format(task_name))
        return jsonify({'info': '提交{}成功'.format(task_name), 'is_success': True})
    except RuntimeError as e:
        server_loger.warning(e)
        return jsonify({'info': '提交{}失败,原因:{}'.format(task_name, e), 'is_success': False})


@app.route('/api/task/suspend/<string:task_name>')
def suspend_task(task_name: str):
    try:
        task_manger.suspend(task_name)
        server_loger.info('task:{}被挂起'.format(task_name))
        return jsonify({'info': '挂起{}成功'.format(task_name), 'is_success': True})
    except RuntimeError as e:
        server_loger.error(e)
        return jsonify({'info': '挂起{}失败,原因:{}'.format(task_name, e), 'is_success': False})


@app.route('/api/task/kill/<string:task_name>')
def kill_task(task_name: str):
    try:
        task_manger.kill(task_name)
        server_loger.info('task:{}被杀死'.format(task_name))
        return jsonify({'info': '杀死{}成功'.format(task_name), 'is_success': True})
    except RuntimeError as e:
        server_loger.error(e)
        return jsonify({'info': '杀死{}失败,原因:{}'.format(task_name, e), 'is_success': False})
    except RuntimeWarning as e:
        server_loger.error(e)
        return jsonify({'info': '杀死{}失败,原因:{}'.format(task_name, e), 'is_success': False})


@app.route('/api/task/start/<string:task_name>')
def start_task(task_name: str):
    try:
        task_manger.resume(task_name)
        server_loger.info('task:{}启动'.format(task_name))
        return jsonify({'info': '启动{}成功'.format(task_name), 'is_success': True})
    except RuntimeError as e:
        server_loger.error(e)
        return jsonify({'info': '启动{}失败,原因:{}'.format(task_name, e), 'is_success': False})
    except RuntimeWarning as e:
        server_loger.exception(e)
        return jsonify({'info': '启动{}失败,原因:{}'.format(task_name, e), 'is_success': False})


# ---------------------------------------
# 数据库查询api
# ---------------------------------------

@app.route('/api/search/illegal/<string:number_plate>')
def illegal_search(number_plate: str):
    """违规查询

    """
    conn = get_connection(DataConfig.DATABASE_PATH)
    result = excute_sql(
        conn,
        'SELECT start_time_id,img_path,criminal_type from criminal where number_plate like ?',
        (number_plate,),
        True
    )
    if result is None:
        server_loger.info('收到对车牌号{}的违规查询'.format(number_plate))
        return jsonify({'info': '为查询到结果', 'is_success': False})
    else:
        start_time_id, img_path, criminal_type = result
        # 解析时间
        start_time_ymd = start_time_id.split(' ')[0]
        start_time_hms = start_time_id.split(' ')[1]
        # 解析图像
        # 首先把static先去除掉
        img_path = [reduce(lambda a, b: a + os.sep + b, path.split(os.sep)[1:]) for path in img_path.split('_')]
        img_path = [url_for('static', filename=path) for path in img_path]
        # 解析违规类型
        illegal_type = criminal_type
        return jsonify({
            'start_time_ymd': start_time_ymd,
            'start_time_hms': start_time_hms,
            'img_path': img_path,
            'illegal_type': illegal_type
        })


if __name__ == "__main__":
    server_loger = get_logger('logs/server.log')
    cfg_data_handler = get_cfgDataHandler()
    img_info_pool = ImgInfoPool(max_size=30)
    task_manger = TaskManager(img_info_pool)
    app.run(port=3001, debug=True)
