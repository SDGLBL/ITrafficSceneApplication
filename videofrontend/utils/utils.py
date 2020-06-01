import os
import platform
import os.path as osp

import mmcv
import numpy as np
import cv2 as cv

from cfg import Cfg
from task.configs import CrossRoadsTaskFakeCfg
from task.configs.crossRoadsTask import CrossRoadsTaskCfg
from utils.logger import get_logger

logger=get_logger()

def get_vehicle_violation_imag_path(Cfg_path, file_name):
    """
    获取文件名的绝路径
    :param img_path: 绝对路径
    :return:
    """
    sys = platform.system()
    curPath = os.path.abspath(os.path.dirname(__file__))
    abs_path = ""
    if sys == "Windows":
        rootPath = curPath[:curPath.find("ITrafficSceneApplication\\") + len(
            "ITrafficSceneApplication\\")]  # 获取myProject，也就是项目的根路径
    else:
        rootPath = curPath[:curPath.find("ITrafficSceneApplication/") + len(
            "ITrafficSceneApplication/")]  # 获取myProject，也就是项目的根路径

    abs_path = osp.join(rootPath, Cfg_path, file_name)
    return abs_path


def get_image_of_video(Cfg_path,video_path, num=100):
    """
     获取制定帧数的图像 ,默认是第一百帧
    :param Cfg_path:配置路径
    :param video_path: 视频路径
    :param num: 第多少帧
    :return: 图像

    """

    img = mmcv.VideoReader(video_path)[num]
    sys = platform.system()

    if sys == "Windows":
        file_name = video_path.split("\\")[-1].replace(".mp4", "") + '.jpg'
    else:
        file_name = video_path.split("/")[-1].replace(".mp4", "") + '.jpg'
    image_path = get_vehicle_violation_imag_path(Cfg_path, file_name)
    cv.imwrite(image_path, img)
    return image_path

def get_mask(img_label,height,width):
    """
    根据场景类型生成相应的mask
    1.路口交通情况检测
    2.路口饱和度检测
    3.高速公路情况检测
    4.其他场景情况检测
    :param img_label:图像标注json
    :param height:图像高
    :param width:图像宽
    :return: 蒙版mask
    """
    #违规占用车道赋值信息记录表
    z_to_y={"小汽车":"car",
            "卡车":"truck",
            "巴士":"bus"}
    task_mask_info = {"isExist": 0,"forbid_info":{}}
    if img_label["label_info"]["scene"]== "1":
        # 违章停车监控组件0或1即可
        print(img_label)
        if "ParkingMonitoringComponent" in img_label["label_info"].keys():
            mask = np.ones((height, width), dtype="uint8")
            task_mask_info["isExist"] = 1
            lane_list=img_label["label_info"]["ParkingMonitoringComponent"]
            for inx,val in enumerate(lane_list):
                pts = np.array(val,np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv.polylines(mask, [pts], True, 0)
                cv.fillPoly(mask, [pts], 0)
            task_mask_info["ParkingMonitoringComponent"]=mask
        if "LaneMonitoringComponent" in img_label["label_info"].keys():
            mask1 = np.ones((height, width), dtype="uint8")
            task_mask_info["isExist"]=1
            park_list = img_label["label_info"]["LaneMonitoringComponent"]
            for inx,val in enumerate(park_list):
                data=[]
                for object_type in val["forbid"]:
                    data.append(z_to_y[object_type])
                task_mask_info["forbid_info"][inx+2]=data
                pts = np.array(val["points"], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv.polylines(mask1, [pts], True, inx+2)
                cv.fillPoly(mask1, [pts], inx+2)
            task_mask_info["LaneMonitoringComponent"] = mask1
            print(task_mask_info)
    elif img_label["label_info"]["scene"]== "2":
        print("2")
    elif img_label["label_info"]["scene"]== "3":
        print("3")
    else:
        print("其他")
    return task_mask_info

def create_task_cfg(task_mask_info,scene_info):
    """
    根据相关信息生成 任务配置
    :param task_mask_info: 蒙版信息如果前端用户选择了违规占用车道U违规停车
    :param scene_info: 场景信息和任务名，还有组件功能列表
    :return: 任务配置
    """
    if scene_info["scene"]=="1":
        # 创建路口场景配置
        create_crossroads_task(task_mask_info, scene_info)



def show_imge(path):
    img = cv.imread(path)
    cv.imshow('frame', img)
    if cv.waitKey(0) == 27:
        cv.destroyAllWindows()

def write_snapshot_image(file_name):
    """
    将执行的任务视频快照存入videofrontend/static/snapshotimages路径下
    :param file_name:
    :return:
    """
    image_path=get_image_of_video(Cfg.snapshot_path,get_vehicle_violation_imag_path(Cfg.video_save_dir,file_name))
    return image_path

def get_image_of_height_width(file_name):
    image_path=get_image_of_video(Cfg.snapshot_path,get_vehicle_violation_imag_path(Cfg.video_save_dir,file_name))
    image=cv.imread(image_path)
    height=image.shape[0]
    width=image.shape[1]
    return height,width

def calculation_task_duration(file_name, time_gap=15):
    """
    计算任务时长 默认间隔为15
    :param file_name:
    :param time_gap:
    :return: Ajax调用间隔单位s
    """
    cap = cv.VideoCapture(get_vehicle_violation_imag_path(Cfg.video_save_dir, file_name))
    # file_path是文件的绝对路径，防止路径中含有中文时报错，需要解码
    if cap.isOpened():  # 当成功打开视频时cap.isOpened()返回True,否则返回False
        # get方法参数按顺序对应下表（从0开始编号)
        rate = cap.get(5)  # 帧速率
        FrameNumber = cap.get(7)  # 视频文件的帧数
        duration = int(FrameNumber / rate / time_gap)  # 帧速率/视频总帧数 是时间，除以60之后单位是分钟

    return duration

def create_crossroads_task(task_mask_info,scene_info):
    """
    创建CrossroadsTask场景
    :param task_mask_info:
    :param scene_info:
    :return:
    """
    for name, component_cfg in CrossRoadsTaskCfg.items():
        if name == 'head':
            component_cfg[0]['filename'] = osp.join('videoData','video',scene_info["file_name"])
        elif name == 'tracker':
            continue
        elif name == 'backbones':
            for backbone in component_cfg:
                for backbone_component_cfg in backbone:
                    cfg_type = backbone_component_cfg['type']
                    if cfg_type == 'PathExtract':
                        backbone_component_cfg['eModelPath'] = osp.join('videoData','video',scene_info["emd_name"])
                    elif cfg_type == 'TrafficStatistics':
                        backbone_component_cfg['eModelPath'] = osp.join('videoData','video',scene_info["emd_name"])
                        if "TrafficStatistics" in scene_info["components"]:
                            backbone_component_cfg['is_process'] = True  # 车流统计模块需要选择是否开启
                    elif cfg_type == 'ParkingMonitoringComponent':
                        if "ParkingMonitoringComponent" in scene_info["components"]:
                            if "ParkingMonitoringComponent" in task_mask_info.keys():
                                backbone_component_cfg['monitoring_area'] = task_mask_info["ParkingMonitoringComponent"]
                                backbone_component_cfg['is_process'] = True
                            else:
                                raise AttributeError('不存在{}蒙版'.format("ParkingMonitoringComponent"))
                    elif cfg_type == 'LaneMonitoringComponent':
                        if "LaneMonitoringComponent" in scene_info["components"]:
                            if "LaneMonitoringComponent" in task_mask_info.keys():
                                backbone_component_cfg['monitoring_area'] = task_mask_info["LaneMonitoringComponent"]
                                backbone_component_cfg['no_allow_car'] = task_mask_info["forbid_info"]
                                backbone_component_cfg['is_process'] = True
                            else:
                                raise AttributeError('不存在{}蒙版'.format("LaneMonitoringComponent"))


def create_crossRoadsTaskFake():
    parking_monitoring_area = np.ones((1080, 1920), dtype=int)
    parking_monitoring_area[400:800, 750:1250] = 0
    lane_monitoring_area = np.ones((1080, 1920), dtype=int)
    lane_monitoring_area[400:800, 750:1250] = 2
    # 如下是一个路口演示demo
    # 因为使用FakeCfg模拟目标探测的效果所以需要在head导入视频路径和已经探测好的json文件
    for name, component_cfg in CrossRoadsTaskFakeCfg.items():
        if name == 'head':
            component_cfg[0]['filename'] = './lot_15.mp4'
            component_cfg[0]['json_filename'] = './lot_15.json'
        elif name == 'tracker':
            continue
        elif name == 'backbones':
            for backbone in component_cfg:
                for backbone_component_cfg in backbone:
                    cfg_type = backbone_component_cfg['type']
                    if cfg_type == 'PathExtract':
                        backbone_component_cfg['eModelPath'] = './lot_15.emd'
                    elif cfg_type == 'TrafficStatistics':
                        backbone_component_cfg['eModelPath'] = './lot_15.emd'
                        backbone_component_cfg['is_process'] = True  # 车流统计模块需要选择是否开启
                    elif cfg_type == 'ParkingMonitoringComponent':
                        backbone_component_cfg['monitoring_area'] = parking_monitoring_area
                        backbone_component_cfg['is_process'] = True
                    elif cfg_type == 'LaneMonitoringComponent':
                        backbone_component_cfg['monitoring_area'] = lane_monitoring_area
                        backbone_component_cfg['no_allow_car'] = {2: ['car']}
                        backbone_component_cfg['is_process'] = True

def reset_crossRoadsTask():
    """
    重置CrossRoadsTask
    :return:
    """
    for backbone in CrossRoadsTaskCfg["backbones"]:
        for backbone_component_cfg in backbone:
            if "is_process" in backbone_component_cfg.keys():
                 backbone_component_cfg["is_process"]=False
            if "eModelPath" in backbone_component_cfg.keys():
                backbone_component_cfg["eModelPath"]=None
            if "monitoring_area" in backbone_component_cfg.keys():
                backbone_component_cfg["monitoring_area"]=None
            if "no_allow_car" in backbone_component_cfg.keys():
                backbone_component_cfg["no_allow_car"]={}
