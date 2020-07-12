import importlib
import os
from copy import deepcopy
from functools import reduce
from os.path import exists, join

import cv2
import mmcv
import json
import platform
import numpy as np
import multiprocessing as mp
from cfg import DataConfig, TaskConfig
from utils.logger import get_logger
from flask import Flask, jsonify, url_for, request
from task import TaskManager, ImgInfoPool, get_cfgDataHandler
from utils.sqlitedao import excute_sql, get_connection
from utils.utils import path2source_path
from werkzeug.utils import secure_filename
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
        # 强制转换读取的路径为资源路径
        video_snapshot_path = path2source_path(video_snapshot_path)
        video_snapshot_paths.append(video_snapshot_path)
    video_infos = [{
        'video_name': video_name,
        'video_snapshot_url': join('/',video_snapshot_path) 
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
        >>> }
    """
    # TODO：此处应该配合manager的信息实时刷新，现在还未实现
    task_list = [
        {
            'task_name': task_name,# task名
            'task_snapshot': path2source_path(join('/',DataConfig.SNAPSHOT_DIR,task_name.split('.')[0]+'.jpg'))# task处理的视频的截图
            # 'task_progress': task_name['task_progress'] # taks进度
        }
        for task_name in task_manger.tasks.keys()
    ]
    server_loger.info('前端获取了task_list:{}'.format(task_list))
    return jsonify(task_list)


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
# url: /api/video/video_info/?video_name=lot_15.mp4 获取视频video_name的信息情况，包括是否环境建模
# url: /api/task/info/analysis/?task_name=lot_15.mp4 获取任务的分析信息，比如违规停车等
# url: /api/task/info/progress/?task_name=lot_15.mp4 获取任务的进度，返回一个1-100的数字
# url: /api/task/info/count/?task_name=lot_15.mp4 获取任务的车流量表格
# ----------------------

@app.route('/api/video/video_info/')
def get_video_info():
    """获取指定视频的视频处理信息

    Args:
        video_name (str): 视频名字。比如：lot_15.mp4

    Returns:

    Examples:
         >>> url = '/api/video/video_info/?video_name=lot15.mp4'
         >>> {
         >>>    'is_exist_emd':True, # 是否存在环境文件
         >>>    'is_exist_json':False # 是否存在json文件
         >>> }
    """
    try:
        video_info = {}
        video_name = request.args.get('video_name')
        if not exists(join(DataConfig.VIDEO_DIR,video_name)):
            raise RuntimeError('不存在名字为{}的视频'.format(video_name))
        if '.' in video_name:
            video_name = video_name.split('.')[0]
        if exists(join(DataConfig.EMODEL_DIR, video_name + '.emd')):
            video_info['is_exist_emd'] = True
        else:
            video_info['is_exist_emd'] = False
        if exists(join(DataConfig.JSON_DIR, video_name + '.json')):
            video_info['is_exist_json'] = True
        else:
            video_info['is_exist_json'] = False
        server_loger.info('前端获取视频{}的信息{}'.format(video_name, video_info))
    except RuntimeError as e:
        server_loger.error(e)
        return jsonify({'info': '获取失败，原因:{}'.format(e), 'is_success': False})
    return jsonify(video_info)



@app.route('/api/task/info/analysis/')
def get_analysis_info_from_pool():
    """获取指定任务的分析信息

    Args:
        task_name (str): [description]

    Returns:
        [type]: [description]

    Examples:
        >>> url = '/api/task/info/analysis/?task_name=lot_15.mp4'
        >>> [
        >>>   {
        >>>     "criminal_img_name": null,
        >>>     "end_time": "2020-05-27 14:14:13",
        >>>     "id": "26.0",
        >>>     "imgs": [],
        >>>     "info_type": "pass",
        >>>     "number_plate": null,
        >>>     "obj_type": "car",
        >>>     "passage_type": "右拐",
        >>>     "start_time": "2020-05-27 14:14:03"
        >>>   }
        >>> ]
    """    
    task_name = request.args.get('task_name')
    try:
        info = task_manger.get_analysis_info(task_name)
        return jsonify(info)
    except RuntimeError as e:
        # server_loger.error(e)
        return jsonify({'info': '获取失败，原因:{}'.format(e), 'is_success': False})

@app.route('/api/task/info/progress/')
def get_progress_info():
    """获取进度信息

    Returns:
        [type]: [description]
    
    Examples:
        >>> url = '/api/task/info/progress/?task_name=lot_15.mp4'
        >>> 12.57
    """    
    task_name = request.args.get('task_name')
    try:
        info = task_manger.get_progress_info(task_name)
        return jsonify(info)
    except RuntimeError as e:
        # server_loger.error(e)
        return jsonify({'info': '获取失败，原因:{}'.format(e), 'is_success': False})

@app.route('/api/task/info/count/')
def get_pass_count_table():
    """获取通行表格

    Returns:
        [type]: [description]
    
    Examples:
        >>> url = '/api/task/info/count/?task_name=lot_15.mp4'
        >>> [
        >>>   [" ","左拐","直行","右拐","总和"],
        >>>   ["car","0.0","3.0","1.0","4.0"],
        >>>   ["truck","0.0","1.0","0.0","1.0"],
        >>>   ["bus","0.0","0.0","0.0","0.0"],
        >>>   [ "总和","0.0","4.0","1.0","5.0"]
        >>> ]
    """    
    task_name = request.args.get('task_name')
    try:
        info = task_manger.get_pass_count_table(task_name)
        return jsonify(info)
    except RuntimeError as e:
        # server_loger.error(e)
        return jsonify({'info': '获取失败，原因:{}'.format(e), 'is_success': False})

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


@app.route('/api/task/submit', methods=['POST'])
def submit_task():
    """提交task
    :return:
    """
    # 先进行数据类型转换
    if request.method != 'POST':
        return jsonify({'info': '提交taskApi只接受POST'})
    try:
        data = request.data
        data = json.loads(data)
        task_name = data["task_name"]
        task_type = data["task_type"]
        if not exists(join(DataConfig.JSON_DIR,task_name.split('.')[0]+'.json')) and 'crossRoads' in task_type:
            get_cfg = importlib.import_module(TaskConfig.MODELLING_CFG_DIR + 'modellingTask').get_injected_cfg
            cfg_data = data["cfg_data"]
            task_cfg = get_cfg(cfg_data)
            task_manger.submit(task_name, task_cfg)
            task_manger.resume(task_name)
            raise RuntimeError('由于该视频的不存在环境建模json文件，本次提交路口场景检测任务失败，系统将会自动启动建模任务请耐心等待建模完成')
        get_cfg = importlib.import_module(TaskConfig.SCENE_CFG_DIR + task_type).get_injected_cfg
        cfg_data = data["cfg_data"]
        task_cfg = get_cfg(cfg_data)
        # 提交任务到task manager
        task_manger.submit(task_name, task_cfg)
        server_loger.info('前端提交了task_name:{}任务'.format(task_name))
        return jsonify({'info': '提交{}成功'.format(task_name), 'is_success': True})
    except RuntimeError as e:
        server_loger.error(e)
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

@app.route('/api/search/illegal/',methods=['GET','POST'])
def illegal_search():
    """违规查询
    查询到的结果为一个list，每个元素为一个字典，包含有一个可能查询到的结果
    Example:
        >>> [
        >>>   {
        >>>     "illegal_type": "illegal_parking",
        >>>     "img_path": [
        >>>       "/static/data/criminal/2020-05-27 14-14-05 23.0 0.jpg",
        >>>       "/static/data/criminal/2020-05-27 14-14-05 23.0 1.jpg"
        >>>     ],
        >>>     "number_plate": "浙DD13G2",
        >>>     "obj_type": "car",
        >>>     "start_time_hms": "14:14:05",
        >>>     "start_time_ymd": "2020-05-27"
        >>>   },
        >>>   {
        >>>     "illegal_type": "illegal_parking",
        >>>     "img_path": [
        >>>       "/static/data/criminal/2020-05-27 14-14-05 23.0 0.jpg",
        >>>       "/static/data/criminal/2020-05-27 14-14-05 23.0 1.jpg"
        >>>     ],
        >>>     "number_plate": "浙DD13G2",
        >>>     "obj_type": null,
        >>>     "start_time_hms": "14:14:05",
        >>>     "start_time_ymd": "2020-05-27"
        >>>   }
        >>> ]
    """
    conn = get_connection(DataConfig.DATABASE_PATH)
    number_plate = request.args.get('number_plate')
    # 如果前端发送的请求参数key错误
    if number_plate is None:
        server_loger.info('收到违规查询请求，但number_plate参数不存在，前端可能发送了错误的参数key')
        return jsonify({'info': '请确保参数key为number_plate', 'is_success': False})
    # 如果发送过来的数据为空
    if number_plate == '':
        server_loger.info('收到违规查询请求，但其查询目标车牌号为空')
        return jsonify({'info': '请确保车牌号不为空', 'is_success': False})
    # 如果发送过来的车牌号长度果断，可能导致列表过长，因此限制最短长度为4
    if len(number_plate) < 4:
        server_loger.info('收到违规查询请求，但其查询目标车牌号长度过短，为防止返回结果过多，不予处理')
        return jsonify({'info': '请确保查询车牌号长度大于等于4，以保证返回list不会过长', 'is_success': False})
    number_plate = "%"+number_plate+"%"
    result = excute_sql(
        conn,
        'SELECT C.start_time_id, C.number_plate, C.img_path, C.criminal_type,T.obj_type FROM criminal AS C LEFT JOIN traffic AS T ON C.start_time_id = T.start_time_id WHERE C.number_plate LIKE ?',
        (number_plate,),
        True
    )
    if result is None or len(result) == 0:
        server_loger.info('收到对车牌号{}的违规查询'.format(number_plate))
        return jsonify({'info': '未查询到结果', 'is_success': False})
    else:
        result_list = []
        for a_result in result:
            start_time_id, number_plate, img_path, criminal_type, obj_type = a_result
            # 解析时间
            start_time_ymd = start_time_id.split(' ')[0]
            start_time_hms = start_time_id.split(' ')[1]
            # 解析图像
            img_path = [join('/',path2source_path(path)) for path in img_path.split('_')]
            # 解析违规类型
            illegal_type = criminal_type
            result_list.append({
            'start_time_ymd': start_time_ymd,
            'start_time_hms': start_time_hms,
            'img_path': img_path,
            'illegal_type': illegal_type,
            'number_plate':number_plate,
            'obj_type':obj_type
            })
        server_loger.info('收到对车牌号{}的违规查询,且查询成功，结果为{}'.format(number_plate,result_list))
        return jsonify(result_list)


# ---------------------------------------
# 上传文件api
# ---------------------------------------
@app.route('/api/video/upload',methods=['POST'])
def upload_file():
    try:
        f = request.files["file"]
        save_path = join(DataConfig.VIDEO_DIR,secure_filename(f.filename))
        server_loger.info('收到文件名为{}的文件上传请求,保存到{}目录'.format(f.filename,DataConfig.VIDEO_DIR))
        f.save(save_path)
        return jsonify({'info': '提交文件成功', 'is_success': True})
    except RuntimeError as e:
        server_loger.error(e)
        return jsonify({'info': '提交文件失败，原因为{}'.format(e), 'is_success': False})

@app.route('/api/vue-admin-template/user/login', methods=['POST'])
def user_login():
    """
    登录验证
    :return: 
    """
    return jsonify({'code': 20000, 'data': 'admin-token'})

@app.route('/api/vue-admin-template/user/info', )
def user_info():
    """
    登录验证
    :return: 
    """
    return jsonify({'code': 20000, 'data': {
    'roles': ['admin'],
    'introduction': 'I am a super administrator',
    'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
    'name': 'Super Admin'}})

@app.route('/api/vue-admin-template/user/logout',methods=['POST'])
def user_logout():
    """
    退出登录
    :return:
    """
    return jsonify({'code': 20000, 'data': 'success'})
    
if __name__ == "__main__":
    # Linux平台启动
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)
    server_loger = get_logger()
    img_info_pool = ImgInfoPool(max_size=30)
    task_manger = TaskManager(img_info_pool)
    app.run(port=3001, debug=True)
