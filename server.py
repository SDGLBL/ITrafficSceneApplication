import os
from functools import reduce
from os.path import exists, join

import cv2
import mmcv
import json
from cfg import DataConfig
from utils.logger import get_logger
from flask import Flask, jsonify, url_for, request
from task import TaskManager,ImgInfoPool,get_cfgDataHandler



app = Flask(__name__)


@app.route('/api/video/video_list')
def get_video_list():
    """获取视频列表以及对应的截图url

    Returns:
        {
            "video_name" : 视频名称。Example: lot_15
            "video_snapshot" : 图像的url路径,。Example: /static/data/video/lot_15.jpg
        }
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
        # 因为video_snapshot_path已经包含了static,因此需要手动去除掉static
        video_snapshot_path = reduce(lambda a, b: a + os.sep + b, video_snapshot_path.split(os.sep)[1:])
        video_snapshot_paths.append(video_snapshot_path)
    video_infos = [{
        'video_name': video_name,
        'video_snapshot_url': url_for('static', filename=video_snapshot_path)
    }
        for video_name, video_snapshot_path in zip(video_names, video_snapshot_paths)]
    return jsonify(video_infos)


@app.route('/api/task/task_list')
def get_task_list():
    """获取后台Task列表

    Returns:
        {
            'task_name': task名
            'task_snapshot_url': task处理的视频的截图
            'task_progress': taks进度
        }
    """
    task_list = [
        {
            'task_name': task['task_name'],  # task名
            'task_snapshot_url': task['task_snapshot_url'],  # task处理的视频的截图
            'task_progress': task['task_progress'] # taks进度
        }
        for task in task_manger.tasks
    ]
    return jsonify(task_list)


@app.route('/api/video/video_info/<string:video_name>')
def get_video_info(video_name: str):
    """获取指定视频的视频处理信息

    Args:
        video_name (str): 视频名字。比如：lot_15.mp4

    Returns:
        {
            'is_exist_emd':是否存在环境模型,
            'is_exist_json':是否存在已经运行过的detector json
        }
    """
    video_info = {}
    video_name = video_name.split('.')[1]
    if not exists(join(DataConfig.EMODEL_DIR, video_name + '.emd')):
        video_info['is_exist_emd'] = 'exist'
    else:
        video_info['is_exist_emd'] = 'no exist'
    if not exists(join(DataConfig.JSON_DIR, video_name + '.json')):
        video_info['is_exist_json'] = 'exist'
    else:
        video_info['is_exist_json'] = 'no exist'
    return jsonify(video_info)


@app.route('/api/video/del/<string:video_name>')
def delete_video(video_name: str):
    """删除指定的video

    Args:
        video_name (str): video的名字 。Example：lot_15.mp4

    Returns:
        {
            'info':'视频已经被移除'
        }
    """
    try:
        os.remove(join(DataConfig.VIDEO_DIR, video_name))
    except FileNotFoundError:
        server_loger.info('删除视频api被调用，指定被删除视频名字为{}，但其已经不存在了'.format(video_name))
        return jsonify({'info': '视频不存在', 'is_success':True})
    return jsonify({'info': '视频已经被移除', 'is_success':True})


@app.route('/api/task/submit', methods=['POST'])
def submit_task():
    """提交task
    :return:
    """
    # 先进行数据类型转换
    if request.method != 'POST':
        return jsonify({'info':'提交taskApi只接受POST'})
    task_cfg_data = request.get_data()
    task_cfg_data = json.loads(task_cfg_data)
    # 提取出task的name
    task_name = task_cfg_data['task_name']
    del task_cfg_data['task_name']
    try:
        # 处理传递来的数据
        task_cfg = cfg_data_handler.handle(task_cfg_data)
        # 提交任务到task manager
        task_manger.submit(task_name,task_cfg)
        jsonify({'info': '提交{}成功'.format(task_name), 'is_success':True})
    except RuntimeWarning as rw:
        server_loger.warning(rw)
        jsonify({'info': '提交{}失败'.format(task_name), 'is_success':False})


@app.route('/api/task/suspend/<string:task_name>')
def suspend_task(task_name: str):
    try:
        task_manger.suspend(task_name)
        jsonify({'info': '挂起{}成功'.format(task_name), 'is_success':True})
    except RuntimeError as e:
        server_loger.error(e)
        jsonify({'info':'挂起{}失败'.format(task_name), 'is_success':False})

@app.route('/api/task/kill/<string:task_name>')
def kill_task(task_name: str):
    try:
        task_manger.kill(task_name)
        jsonify({'info': '杀死{}成功'.format(task_name), 'is_success':True})
    except RuntimeError as e:
        server_loger.error(e)
        jsonify({'info': '杀死{}失败'.format(task_name), 'is_success':False})
    except RuntimeWarning as e:
        server_loger.error(e)
        jsonify({'info': '杀死{}失败,请不要杀死已经被杀死的task'.format(task_name), 'is_success':False})


@app.route('/api/task/start/<string:task_name>')
def start_task(task_name: str):
    try:
        task_manger.resume(task_name)
        jsonify({'info': '启动{}成功'.format(task_name), 'is_success':True})
    except RuntimeError as e:
        server_loger.error(e)
        jsonify({'info': '启动{}失败'.format(task_name), 'is_success':False})
    except RuntimeWarning as e:
        server_loger.exception(e)
        jsonify({'info': '启动{}失败,请不要重复启动已经启动了的task'.format(task_name), 'is_success':False})

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
        jsonify({'info': '获取失败，{}task还为存储信息'.format(task_name), 'is_success':False})


if __name__ == "__main__":
    server_loger = get_logger('logs/server.log')
    cfg_data_handler = get_cfgDataHandler()
    img_info_pool = ImgInfoPool(max_size=30)
    task_manger = TaskManager(img_info_pool)
    app.run(port=3001, debug=True)
