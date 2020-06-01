import datetime
import json
import multiprocessing as mp
import platform
from queue import Empty
from threading import Thread

from django.views.decorators.csrf import csrf_exempt

from task.build import TaskBuilder
from task.configs.chenxiaotask import ChenXiaoTaskCfg
from django.shortcuts import render,get_object_or_404
from django.urls import reverse
from django.http import Http404, HttpResponse,JsonResponse
from multiprocessing import Process,Pipe
from videofrontend.utils.utils import *
# Create your views here.


##通信队列
from videofrontend.datamaintain import DataMaintenance


def read_info_from_task(mqs):

    i=0
    try:
        while True:
            for mq in mqs:
                img_info = mq.get(timeout=5)
                DataMaintenance.vehicle_volume_dao.set_vehicle_violation_statistics(img_info)
                DataMaintenance.car_volume_dao.set_pass_count_table_statistics(img_info)

    except Empty:
        print('Task结束')
        DataMaintenance.init_data()


@csrf_exempt
def task_start(task):
    """
    执行一个Task
    :param task: 不同场景要做的任务
    :return:
    """
    mqs = task.build()
    task.start()
    readt = Thread(target=read_info_from_task, args=(mqs,))
    readt.start()
    readt.join()

@csrf_exempt
def index(request):
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)
    task = TaskBuilder(ChenXiaoTaskCfg)
    mytask = Process(target=task_start, args=(task,))
    mytask.start()
    return JsonResponse({"isSuccess": 0})

@csrf_exempt
def start(request):
    """
    给播放的接口用来执行Task
    url:http://127.0.0.1:8000/videofrontend/starttask
    :param request:
    :return:
    """
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)

    #if DataMaintenance.submit_task_success:
    if DataMaintenance.task_info["scene_info"]["scene"] == "1":
        if Cfg.task_selected == "crossRoadsTaskFake":
            # 假配置初始化
            create_crossRoadsTaskFake()
            task = TaskBuilder(CrossRoadsTaskFakeCfg)
            mytask = Process(target=task_start, args=(task,))
            mytask.start()
            return JsonResponse({"isSuccess": 1})
        elif Cfg.task_selected == "crossRoadsTask":
            task = TaskBuilder(CrossRoadsTaskCfg)
            mytask = Process(target=task_start, args=(task,))
            mytask.start()
            return JsonResponse({"isSuccess": 1})
        else:
            raise Exception('请检查{}配置是否正确'.format(Cfg.task_selected))
            return JsonResponse({"isSuccess": 0})
    else:
        return JsonResponse({"isSuccess": 0})

@csrf_exempt
def get_traffic_volume_statistics(request):
    """
    实时查询车流量信息
    状态：弃用
    url:http://127.0.0.1:8000/videofrontend/carsvolume
    :param request:
    :return:

    """
    if request.method == "GET":
        datas=DataMaintenance.car_volume_dao.get_traffic_volume_statistics()
        return JsonResponse(datas)
    else:
        return render(request,"video/404.html",None)

@csrf_exempt
def get_traffic_volume_line_chart_statistics(request):
    """
    获取当前任务折线图数据
    url:http://127.0.0.1:8000/videofrontend/carsvolumelinechart?task_name=lot_15.mp4
    :param request:
    :return: 折线图数据
    """

    if request.method == "GET":
        task_name=request.GET.get("task_name")
        DataMaintenance.car_volume_dao.get_traffic_volume_line_chart_statistics(task_name,
                                                                                     DataMaintenance.line_chart_datas)
        #DataMaintenance.line_chart_datas.append(data)
        datas={"option":DataMaintenance.line_chart_datas}
        return JsonResponse(datas)
    else:
        return JsonResponse({"isExist":0})
@csrf_exempt
def get_vehicle_violation_statistics(request):
    """
    实时获取当前违规信息记录
    url:http://127.0.0.1:8000/videofrontend/vehicleviolation
    :param request:
    :return: 违规信息记录
    """

    if request.method == "GET":
        datas=DataMaintenance.vehicle_volume_dao.get_vehicle_violation_statistics()
        return  JsonResponse(datas)
    else:
        return JsonResponse({"isExist":0})

@csrf_exempt
def get_task_list(request):
    """
    获取任务列表
    url:http://127.0.0.1:8000/videofrontend/tasklist
    :param request:
    :return: 任务列表
    """

    if request.method == "GET":
        datas=DataMaintenance.car_volume_dao.get_task_list()
        print(datas)
        return  JsonResponse(datas)
    else:
        return  JsonResponse({"isExist":0})

@csrf_exempt
def get_vehicle_violation_by_number_plate(request):
    """
    根据车牌号查询和任务名查询违规信息
    url:http://127.0.0.1:8000/videofrontend/violationinfo?number_plate='浙DD13G2'
    :param request:
    :return: 违规车辆相关信息
    """
    if request.method == "GET":
        number_plate=request.GET.get("number_plate")

        datas=DataMaintenance.vehicle_volume_dao.get_vehicle_violation_by_number_plate(number_plate)
        return JsonResponse(datas)
    else:
        return  JsonResponse({"isExist":0})

@csrf_exempt
def get_history_traffic_volume_line_chart(request):
    """
    根据任务名 查询违规历史折线图信息
    状态：启用
    url:http://127.0.0.1:8000/videofrontend/historylinechart?task_name=lot_15.mp4
    :param request:
    :return:违规历史折线图信息

    """

    if request.method == "GET":
        task_name=request.GET.get("task_name")
        datas=DataMaintenance.car_volume_dao.get_history_traffic_volume_line_chart(task_name)
        return JsonResponse(datas)
    else:
        return JsonResponse({"isExist":0})

@csrf_exempt
def get_pass_count_table_statistics(request):
    """
    实时获取车流量信息表
    url:http://127.0.0.1:8000/videofrontend/passcounttable
    :param request:
    :return: 车流量信息表数据
    """

    if request.method == "GET":
        datas=DataMaintenance.car_volume_dao.get_pass_count_table_statistics()

        return JsonResponse(datas)
    else:
        return JsonResponse({"isExist":0})
@csrf_exempt
def get_real_time_vehicle_statistics(request):
    """
    获取实时车辆信息(pass)
    url:http://127.0.0.1:8000/videofrontend/realtimevehicleinfo
    状态：弃用
    :param request:
    :return: 实时车辆信息列表
    """
    if request.method == "GET":
        datas = DataMaintenance.car_volume_dao.get_real_time_vehicle_statistics()
        return JsonResponse(datas)
    else:
        return render(request, "video/404.html", None)

@csrf_exempt
def submit_scene_info(request):
    """
    前端向后端提交文件名和执行场景信息和开启的功能组件
    url:http://127.0.0.1:8000/videofrontend/submitsceneinfo
    :return: 根据场景进行判断，1 ，3，4就要返回待标注的图像(绝对路径),目前只做了1先写1
    """

    img_path=""
    if request.method == "POST":
        scene_info=json.loads(request.body)
        if scene_info["scene"]=="1":
            if os.path.exists(osp.join('videoData','video',scene_info["file_name"])) \
                    and os.path.exists(osp.join('videoData','video',scene_info["emd_name"])):
                DataMaintenance.car_volume_dao.set_task(scene_info["file_name"])
                video_path=osp.join('videoData','video',scene_info["file_name"])
                #返回待标注图像路径
                img_path=get_image_of_video(Cfg.frame_image_save_dir,video_path)
                DataMaintenance.task_info["scene_info"]=scene_info
                invoke_duration=calculation_task_duration(scene_info["file_name"])
                return JsonResponse({"img_path":img_path,"isExist":1,"invoke_duration":invoke_duration})
            else:
                raise FileNotFoundError('未找到{}或{}文件'.format(osp.join('videoData', 'video', scene_info["file_name"]),
                                                            osp.join('videoData', 'video', scene_info["emd_name"])))
        else:
            return JsonResponse({"img_path":img_path,"isExist": 0})
    else:
        return JsonResponse({"isExist:0"})


@csrf_exempt
def submit_task(request):
    """
    提交任务
    url:http://127.0.0.1:8000/videofrontend/submittask
    :param request:
    :return: 任务是否提交成功
    """

    if request.method == "POST":
        img_label = json.loads(request.body)
        print("标注信息返回")
        print(img_label)
        datas = {"label_info": img_label}
        # 将视频快照保存在snapshotimages文件夹
        write_snapshot_image(
            get_vehicle_violation_imag_path(Cfg.video_save_dir, DataMaintenance.task_info["scene_info"]["file_name"]))

        # 图像高宽列表
        height, width = get_image_of_height_width(DataMaintenance.task_info["scene_info"]["file_name"])
        task_cfg_info = get_mask(datas, height, width)
        print("任务配置信息")
        print(task_cfg_info)
        create_task_cfg(task_cfg_info, DataMaintenance.task_info["scene_info"])
        DataMaintenance.submit_task_success = True
        return JsonResponse({"isExist": 1})
    else:
        return JsonResponse({"isExist": 0})

