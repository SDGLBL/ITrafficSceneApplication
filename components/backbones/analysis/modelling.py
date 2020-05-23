from utils.analysistools import *
import numpy as np
import math
import pickle
from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT

@BACKBONE_COMPONENT.register_module
class Modelling(BaseBackboneComponent):
    def __init__(self, mainClass=None, speedLenTh=5, dataNum=50000, mapSize=None, stopTh=0.1, sigma=1, modelPath='test.emd'):
        self.paths = []
        self.speeds = []
        self.avgBbox = 0
        if mainClass is None:
            self.mainClass = ['car']
        self.speedLenTh = speedLenTh
        self.dataNum = dataNum
        self.mapSize = mapSize
        self.stopTh = stopTh
        self.sigma = sigma
        self.modelPath = modelPath

    def dataPreparation(self, img, img_info):
        if self.mapSize is None:
            self.mapSize = img_info['shape'][0:2]
            print('图片大小：' + str(self.mapSize))
        for path in img_info['end_path']:
            path['speeds'] = [None]
            if path['cls_name'] not in self.mainClass:
                continue    # 只处理要求的类
            for i in range(1, len(path['dots'])):
                dot0 = path['dots'][i-1]
                dot1 = path['dots'][i]
                i0 = path['indexs'][i-1]
                i1 = path['indexs'][i]
                speedX = (dot1[0] - dot0[0])/(i1-i0)
                speedY = (dot1[1] - dot0[1])/(i1-i0)
                speedLen = vLen([speedX, speedY])
                speedDir = getDirection([speedX, speedY])
                path['speeds'].append([speedX, speedY, speedLen, speedDir])
                self.speeds.append([speedX, speedY, speedLen, speedDir])
                bbox = path['bboxs'][i]
                avgBbox = getAvgBbox(bbox)
                if avgBbox == 0:
                    self.avgBbox += avgBbox
                else:
                    self.avgBbox += avgBbox
                    self.avgBbox = self.avgBbox/2
            self.paths.append(path)

    def makeModel(self):
        # step1 利用统计得到的速度信息得到基向量
        speeds = np.array(self.speeds)
        speedDirs = speeds[:, 3:4]
        axis = getAxis(speedDirs)
        axis0 = axis[0]
        axis1 = axis[1]
        mainAxis = axis0 if abs(axis0) > abs(axis1) else axis1
        secondAxis = axis0 if abs(axis0) < abs(axis1) else axis1
        if mainAxis > 0:
            mainAxis -= math.pi / 2
        print('主轴倾角：' + str(mainAxis) + ',辅轴倾角：' + str(secondAxis))
        transformMat, invTransformMat = getTransformMat([mainAxis, secondAxis])

        # step2 算出特征路径，对数据进行过滤和分类
        importPaths = []
        longPaths = []
        for path in self.paths:
            path = straighten(path, stepTh=self.avgBbox*self.stopTh)  # 过滤掉停止点
            if len(path['zipDots']) > 50:
                path = pathFitting(path, invTransformMat)
                # 得到最大位移，进行方向判定：
                tMain = path['fun_dots'][:, 0]
                tD = tMain[-1] - tMain[1]
                if tD > 2 * self.avgBbox:
                    importPaths.append(path)
                longPaths.append(path)

        # step3 提取重要数据
        # 3.1 提取车道数
        startVar = []
        for path in importPaths:
            startVar.append(path['fun_dots'][0, 1])
        startVar = np.array(startVar)
        laneNum, _ = gaussianCumulative(startVar, self.avgBbox * self.sigma)
        print('车道数：' + str(laneNum))
        startK = KMeans(n_clusters=laneNum)
        startK.fit(startVar[:, np.newaxis])

        # 3.2 提取出口方向数：
        endVar = []
        for path in importPaths:
            endVar.append(path['fun_dots'][-1, 1])
        endVar = np.array(endVar)
        dirNum, _ = gaussianCumulative(endVar, self.avgBbox * self.sigma)
        print('出口方向数：' + str(dirNum))
        endK = KMeans(n_clusters=dirNum)
        endK.fit(endVar[:, np.newaxis])

        # step4 生成模型：
        # step3.1 主区域蒙版
        stopMap, speedMap = getMap(importPaths, self.mapSize, self.avgBbox / 100)

        # step3.2 各车道蒙版
        lanePaths = {}
        for i in range(laneNum):
            lanePaths[i] = []
        for path in importPaths:
            cls = startK.predict([[path['fun_dots'][0, 1]]])[0]
            lanePaths[cls].append(path)

        laneMaps = {}
        for i in lanePaths:
            tStopMap, tSpeedMap = getMap(lanePaths[i], self.mapSize, self.avgBbox / 100)
            laneMaps[i] = {
                'speedMap': tSpeedMap,
                'stopMap': tStopMap
            }

        # step3.3 得各车道停止点
        stopDots = []
        for i in laneMaps:
            tStopMap = laneMaps[i]['stopMap']
            index = np.argmax(tStopMap)
            y = index // tStopMap.shape[1]
            x = index - y * tStopMap.shape[1]
            # 加上偏移量：
            x = int(x + self.avgBbox * math.cos(mainAxis) * 0.5)
            y = int(y + self.avgBbox * math.sin(mainAxis) * 0.5)
            stopDots.append([x, y])

        # step3.4 得到停止线：
        stopLine = [0, 0]
        if len(stopDots) == 1:
            stopDot = stopDots[0]
            k = math.tan(secondAxis)
            b = stopDot[0] - k*stopDot[1]
            stopLine = [k, b]
        elif len(stopDots) > 1:
            stopDots = np.array(stopDots)
            ys = stopDots[:, 1]
            xs = stopDots[:, 0]
            arg = np.polyfit(xs, ys, 1)
            k = arg[0]
            b = arg[1]
            stopLine = [k, b]
        else:
            print('警告：未找到任何停止点！无法得到停止线')

        # 计算出入口可达矩阵
        reachableMat = np.zeros((int(laneNum), int(dirNum)))
        for path in importPaths:
            lane = startK.predict([[path['fun_dots'][0, 1]]])[0]
            dir = endK.predict([[path['fun_dots'][-1, 1]]])[0]
            reachableMat[lane][dir] += 1
        reachableMat = reachableMat > np.max(reachableMat)/10
        print('可达矩阵: ')
        print(reachableMat)

        # 储存：
        model = {
            'type': 'crossroad',
            'avg_bbox':self.avgBbox ,
            'main_axis': mainAxis,
            'second_axis': secondAxis,
            'transform_mat': transformMat,
            'inv_transform_mat': invTransformMat,
            'main_map': speedMap,
            'stop_line': stopLine,
            'lane_maps': laneMaps,
            'lane_classifier': startK,
            'dir_classifier': endK,
            'reachable_mat':reachableMat
        }
        with open(self.modelPath, 'wb') as f:
            pickle.dump(model, f)

    def process(self, **kwargs):
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        for img, img_info in zip(imgs, imgs_info):
            self.dataPreparation(img, img_info)
        print('数据收集进度：{}/{}'.format(str(len(self.speeds)), str(self.dataNum)))
        # 建模开始
        if len(self.speeds) > self.dataNum:
            self.makeModel()
            print('建模完毕，关闭进程')
            exit()

        return kwargs
