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
    url:http://127.0.0.1:8000/videofrontend/carsvolumelinechart
    :param request:
    :return: 折线图数据
    """

    if request.method == "GET":
        data=DataMaintenance.car_volume_dao.get_traffic_volume_line_chart_statistics()
        DataMaintenance.line_chart_datas.append(data)
        datas={"line_char_data":DataMaintenance.line_chart_datas}
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
