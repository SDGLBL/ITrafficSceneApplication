import numpy as np
import cv2
import math
import matplotlib.pyplot as plt
import scipy.signal as signal
from sklearn.cluster import KMeans
from .tools import projection, get_centre


class speedMap:
    def __init__(self, mainAxis=math.pi/2, secondaryAxis=0, avgBbox=99, stopThreshold=0.2, mapSize=(1080, 1920)):
        """初始化函数

        Keyword Arguments:
            mainAxis {float} -- 主轴方向 (default: {math.pi/2})
            secondaryAxis {int} -- 辅轴方向 (default: {0})
            avgBbox {int} -- 方框平均大小 (default: {99})
            stopThreshold {float} -- 停止阈值 (default: {0.2})
            mapSize {tuple} -- 图像大小 (default: {(1080, 1920)})
        """        
        self.mapSize = mapSize
        self.speedMapMain = np.zeros(self.mapSize, dtype=float)
        self.stopMap = np.zeros(self.mapSize, dtype=float)
        self.mainAxis = mainAxis
        self.secondaryAxis = secondaryAxis
        self.stopThreshold = stopThreshold
        self.avgBbox = avgBbox

    def update(self, path: dict):
        """更新地图

        Arguments:
            path {dict} -- 待处理路径
        """        

        for i in range(1, len(path['bboxs'])):
            t_bbox = path['bboxs'][i]
            t_speed = path['speed'][i]
            t_speed = self.speedResolve(t_speed[0], t_speed[1])
            self.mapUpdate(t_bbox, t_speed)
            #break

    def mapUpdate(self, bbox, speed):
        """map更新函数，更新speedMapMain 和 stopMap

        Arguments:
            bbox {[list]} -- 更新范围
            speed {[list]} -- speed[0] 表示沿mainAxis方向分解的速度。speed[1]沿secondaryAxis方向分解的速度 
        """

        # 如果主方向上的速度大于辅方向，则将速度累加到主速度地图上
        if speed[0] > speed[1]:
            self.speedMapMain = self.maskAdd(bbox, speed[0], self.speedMapMain)
        if speed[0] < self.stopThreshold and speed[1] < self.stopThreshold:
            self.stopMap = self.maskAdd(bbox, 1, self.stopMap, t=0.1)

    def maskAdd(self, bbox, speed, map, t=0.7):
        """map的bbox框内叠加

        Arguments:
            bbox {list} -- 略
            speed {float} -- 待叠加的数字
            map {np.narray} -- 待更新的地图

        Keyword Arguments:
            t {float} -- bbox的缩放比例 (default: {0.7})

        Returns:
            np.narray -- 返回修改后的map
        """        
        c = get_centre(bbox)
        h = bbox[3] - bbox[1]
        w = bbox[2] - bbox[0]
        h = h * t / 2
        w = w * t / 2

        map[int(c[1] - h):int(c[1] + h), int(c[0] - h):int(c[0] + h)] += speed
        return map

    def getMainMask(self, direction:bool=True, th=0.3): 
        """得到关键区域

        Keyword Arguments:
            direction {bool} -- 速度方向，默认为远离摄像头方向 (default: {True})
            th {float} -- 阈值，0.3表示取出该地图中大于 0.3倍最大值的数据制成蒙版，一般th越小，蒙版区域越大(default: {0.1})
            updata {bool} -- 表示是否更新，为True表示无论曾经是否生成过都重新生成
        Returns:
            [type] -- [description]
        """      
        map = self.speedMapMain
        mainMask = np.zeros(self.mapSize, dtype=np.uint8)
        if self.mainAxis > 0:
            direction = not direction
        if direction:
            th = np.max(map) * th
            mainMask[map > th] = 255
        else:
            th = np.max(-map) * th
            mainMask[map < -th] = 255
        return mainMask

    def getStopMask(self, th=0.5, adjust = 0.5):
        mainMask = self.getMainMask(th=0.1)
        stopMask = np.zeros(self.mapSize, dtype=np.uint8)
        # 得到蒙版区域
        map = self.stopMap
        map[mainMask==0] = 0      # 只关心关键区域的
        th = np.max(map) * th
        stopMask[map > th] = 255

        # 得到最值坐标
        index = np.argmax(map)
        y = index//map.shape[1]
        x = index - y*map.shape[1]
        # print([x,y])
        cv2.circle(stopMask, (x,y), 5, 125,thickness=-1)

        # 为最大值增加一个偏移量：
        # print(self.avgBbox)

        x = int(x + self.avgBbox * math.cos(self.mainAxis)*adjust)
        y = int(y + self.avgBbox * math.sin(self.mainAxis)*adjust)
        cv2.circle(stopMask, (x,y), 5, 200,thickness=-1)

        # 绘制停止线：
        k = math.tan(self.secondaryAxis)
        b = y - k*x
        dot1 = (0, int(b))
        dot2 = (int(self.mapSize[1]), int(k*self.mapSize[1]+b))
        cv2.line(stopMask,dot1,dot2,255,4)

        return stopMask
        
    def speedResolve(self, sx, sy):
        """将速度方向延主轴，辅轴方向分解

        Arguments:
            sx {float} -- x方向速度
            sy {float} -- y方向速度

        Returns:
            list -- [主轴方向速度, 辅轴方向速度]
        """        
        main_w = projection([sx,sy], self.mainAxis)
        secondary_w = projection([sx,sy], self.secondaryAxis)
        return [main_w, secondary_w]

    def profile_map(self):
        """得到最佳主地图最佳剖面

        Returns:
            list -- 剖面数据
        """        
        map = self.speedMapMain
        index = np.argmax(map)
        i0 = index//map.shape[1]
        i1 = i0*map.shape[1] - index
        data = map[i0, :]
        data = signal.medfilt(data, 2*(self.avgBbox//2)+1)
        return data

    def getStopLine(self, adjust=0.5):
        mainMask = self.getMainMask(th=0.1)
        tStopMask = np.zeros(self.mapSize, dtype=float)
        tStopMask[mainMask!=0] = self.stopMap[mainMask!=0]       # 只关心关键区域的
        index = np.argmax(tStopMask)
        y = index//tStopMask.shape[1]
        x = index - y*tStopMask.shape[1]

        # 加上偏移量：
        x = int(x + self.avgBbox * math.cos(self.mainAxis)*adjust)
        y = int(y + self.avgBbox * math.sin(self.mainAxis)*adjust)

        # 得到k、b的值：
        k = math.tan(self.secondaryAxis)
        b = y - k*x
        return k,b
