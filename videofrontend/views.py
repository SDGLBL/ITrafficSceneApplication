import datetime
import json
import os
import random
import time
from queue import Empty, Queue

import cv2
import redis
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.views import generic
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
                del img_info
                i=i+1
                img_info = {'pass_count': i,
                            'left_pass_count': '25',
                            'right_pass_count': '26',
                            'straight_pass_count': '30',
                            'car_pass_count': '5',
                            'truck_pass_count': '8',
                            'bus_pass_count': '23'}
                DataMaintenance.car_volume_dao.set_traffic_volume_statistics(img_info)
                DataMaintenance.vehicle_volume_dao.set_vehicle_violation_statistics(img_info)

    except Empty:
        print('Task结束')
        DataMaintenance.init_data()

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


def index(request):

    return render(request,'video/index.html',None)


def start(request):
    """
    给播放的接口用来执行Task
    :param request:
    :return:
    """
    if platform.system() == 'Linux':
        mp.set_start_method('spawn', force=True)

    ChenXiaoTaskCfg['head'][0]['filename'] = './test.mp4'
    task = TaskBuilder(ChenXiaoTaskCfg)
    mytask = Process(target=task_start, args=(task,))
    mytask.start()
    return HttpResponse("成功执行Task..")

@csrf_exempt
def get_image_of_video_view(request):
    """
    返回制定帧的图像1,3,4需要
    ulr:http://127.0.0.1:8000/videofrontend/imageofvideo
    """
    #TODO:处理返回帧
    if request.method == 'GET':
        #data=json.loads(request.body)
        file_name='test.mp4'
        #记录任务提交
        DataMaintenance.car_volume_dao.set_task(file_name)
        abs_path =get_vehicle_violation_imag_path(Cfg.video_save_dir,file_name)
        num=1
        DataMaintenance.scene_number=num
        image_path=get_image_of_video(abs_path)

    return HttpResponse(image_path)



def get_traffic_volume_statistics(request):
    """
    实时查询车流量信息
    url:http://127.0.0.1:8000/videofrontend/carsvolume
    :param request:
    :return:

    """
    if request.method == "GET" and request.is_ajax():
        datas=DataMaintenance.car_volume_dao.get_traffic_volume_statistics()
        return JsonResponse(datas)
    else:
        return render(request,"video/404.html",None)

def get_traffic_volume_line_chart_statistics(request):
    """
    获取当前任务折线图数据
    url:http://127.0.0.1:8000/videofrontend/carsvolumelinechart?task_name=lot_15.mp4
    :param request:
    :return: 折线图数据
    """

    if request.method == "GET":
        task_name=request.GET.get("task_name")
        data=DataMaintenance.car_volume_dao.get_traffic_volume_line_chart_statistics(task_name,
                                                                                     DataMaintenance.line_chart_datas)
        #DataMaintenance.line_chart_datas.append(data)
        datas={"option":DataMaintenance.line_chart_datas}
        return JsonResponse(datas)
    else:
        return render(request,"video/404.html",None)

def get_vehicle_violation_statistics(request):
    """
    实时获取当前违规信息记录
    url:http://127.0.0.1:8000/videofrontend/vehicleviolation
    :param request:
    :return: 违规信息记录
    """

    if request.method == "GET" and request.is_ajax():
        datas=DataMaintenance.vehicle_volume_dao.get_vehicle_violation_statistics()
        return  JsonResponse(datas)
    else:
        return render(request,"video/404.html",None)


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
        return  render(request,"video/404.html",None)


def get_vehicle_violation_by_number_plate(request):
    """
    根据车牌号查询和任务名查询违规信息
    url:http://127.0.0.1:8000/videofrontend/violationinfo?number_plate='浙DD13G2'
    :param request:
    :return:
    """
    if request.method == "GET":
        number_plate=request.GET.get("number_plate")

        datas=DataMaintenance.vehicle_volume_dao.get_vehicle_violation_by_number_plate(number_plate)
        return JsonResponse(datas)
    else:
        return  render(request,"video/404.html",None)


def get_history_traffic_volume_line_chart(request):
    """
    根据任务名，起始时间，结束时间。查询违规历史折线图信息
    url:http://127.0.0.1:8000/videofrontend/historylinechart?task_name=lot_15.mp4&start_time=2020-05-26 22:30:31&end_time=2020-05-26 22:30:44
    :param request:
    :return: 时间间隔内的违规历史折线图信息
    """

    if request.method == "GET":
        task_name=request.GET.get("task_name")
        start_time=request.GET.get("start_time")
        end_time=request.GET.get("end_time")
        datas=DataMaintenance.car_volume_dao.get_history_traffic_volume_line_chart(task_name,start_time,end_time)
        return JsonResponse(datas)
    else:
        return render(request,"video/404.html",None)


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
        return render(request, "video/404.html", None)

def get_real_time_vehicle_statistics(request):
    """
    获取实时车辆信息(pass)
    url:http://127.0.0.1:8000/videofrontend/realtimevehicleinfo
    :param request:
    :return: 实时车辆信息列表
    """
    if request.method == "GET":
        datas = DataMaintenance.car_volume_dao.get_real_time_vehicle_statistics()
        return JsonResponse(datas)
    else:
        return render(request, "video/404.html", None)
