import os
import platform
import os.path as osp

import mmcv
import numpy as np
import cv2 as cv

from cfg import Cfg


def get_vehicle_violation_imag_path(Cfg_path,file_name):
    """
    获取文件名的绝路径
    :param img_path: 绝对路径
    :return:
    """
    sys=platform.system()
    curPath = os.path.abspath(os.path.dirname(__file__))
    abs_path=""
    if sys=="Windows":
        rootPath = curPath[:curPath.find("ITrafficSceneApplication\\") + len("ITrafficSceneApplication\\")]  # 获取myProject，也就是项目的根路径
    else:
        rootPath = curPath[:curPath.find("ITrafficSceneApplication/") + len(
            "ITrafficSceneApplication/")]  # 获取myProject，也就是项目的根路径

    abs_path = osp.join(rootPath,Cfg_path,file_name)
    return abs_path


def get_image_of_video(video_path,num=100):
    """
    获取制定帧数的图像 ,默认是第一百帧
    :param video_path: 视频路径
    :param num: 第多少帧
    :return: 图像
    """

    img = mmcv.VideoReader(video_path)[num]
    sys=platform.system()

    if sys=="Windows":
        file_name = video_path.split("\\")[-1].replace(".mp4", "") + '.jpg'
    else:
        file_name = video_path.split("/")[-1].replace(".mp4", "") + '.jpg'
    image_path=get_vehicle_violation_imag_path(Cfg.frame_image_save_dir,file_name)
    cv.imwrite(image_path,img)
    return image_path

def get_mask(scene_type):
    """
    根据场景类型生成相应的mask
    1.路口交通情况检测
    2.路口饱和度检测
    3.高速公路情况检测
    4.其他场景情况检测
    :param scene_type:
    :return:
    """

def show_imge(path):
    img=cv.imread(path)
    cv.imshow('frame',img)
    if cv.waitKey(0)==27:
        cv.destroyAllWindows()


def calculation_task_duration(file_name,time_gap=15):
    """
    计算任务时长 默认间隔为15
    :param file_name:
    :param time_gap:
    :return: Ajax调用间隔单位s
    """
    cap = cv.VideoCapture(get_vehicle_violation_imag_path(Cfg.video_save_dir,file_name))
    # file_path是文件的绝对路径，防止路径中含有中文时报错，需要解码
    if cap.isOpened():  # 当成功打开视频时cap.isOpened()返回True,否则返回False
        # get方法参数按顺序对应下表（从0开始编号)
        rate = cap.get(5)  # 帧速率
        FrameNumber = cap.get(7)  # 视频文件的帧数
        duration = int(FrameNumber / rate / time_gap)  # 帧速率/视频总帧数 是时间，除以60之后单位是分钟

    return duration

if __name__=='__main__':
    height=1366
    width=768
    img=np.ones((height, width, 3),dtype="uint8")*255
    pts = np.array([
        [
          614.8936170212766,
          701.063829787234
        ],
        [
          963.8297872340424,
          707.4468085106382
        ],
        [
          993.6170212765957,
          718.0851063829787
        ],
        [
          996.8085106382978,
          709.5744680851063
        ],
        [
          1590.4255319148936,
          717.0212765957447
        ],
        [
          1600.0,
          730.8510638297872
        ],
        [
          637.2340425531914,
          714.8936170212766
        ]
      ], np.int32)
    pts1= np.array([
        [
          1133.1707317073171,
          554.6341463414634
        ],
        [
          1160.4878048780488,
          645.8536585365854
        ],
        [
          1207.8048780487807,
          647.3170731707318
        ],
        [
          1177.5609756097563,
          557.0731707317074
        ]
      ], np.int32)
    pts=pts.reshape((-1,1,2))
    pts1=pts1.reshape((-1,1,2))
    cv.polylines(img,[pts],True,(0,0,0))
    cv.fillPoly(img,[pts],(0,0,0))
   # cv.polylines(img, [pts1], True, (0, 0, 0))
   # cv.fillPoly(img,[pts1],(0,0,0))

    abs_path=get_vehicle_violation_imag_path(Cfg.img_save_dir,"2020-05-18 14-37-47 23 1.jpg")
    #show_imge(abs_path)
    abs_path="D:\\python_work\\ITrafficSceneApplication\\test.mp4"

    path=get_image_of_video(abs_path)
    img=cv.imread('../static/images/100.jpg',-1)
    print(img)

