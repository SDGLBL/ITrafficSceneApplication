from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT
from .tools import get_centre,vLen, getDirection, getAvgBbox
from .speedMap import speedMap
from .eModel import eModel
from scipy import stats
from sklearn.cluster import KMeans
import cv2
import pickle


@BACKBONE_COMPONENT.register_module
class infoPort(BaseBackboneComponent):
    def __init__(self, modelName='lot_15', speedTh=10, pathLTh=5, minDataSize=5000):
        self.tPaths = {}                # 路径缓存池
        self.highGradePaths = []        # 优质路径收集
        self.highGradeSpeed = []        # 优质速度矢量收集
        self.speedTh = speedTh          # 速度阈值，超过该速度才会被保存
        self.pathLTh = pathLTh          # 路径长度阈值，超过该长度才会被保存
        self.minDataSize = minDataSize  # 表示需要收集的最小数据量，用highGradeSpeed的长度进行评估
        self.sMap = None
        self.avgBbox = 99               # 平均大小
        self.mainMapSavePath = './mainMap.jpg'      # 速度图保存地址
        self.stopMapSavePath = './stopMap.jpg'      # 停止图保存地址
        self.classFilter = [2]          # 只对classFilter中的类别进行统计
        self.modelName = modelName

    def img_info2Path(self, img_info):
        """整合img_info，将之转换为路径的形式

        Arguments:
            img_info {dict} -- 略
        """        
        for obj in img_info['objects']:
            t_id = obj['id']
            if t_id not in self.tPaths.keys():
                self.tPaths[t_id] = {
                    'id':t_id,
                    # 该列表所有元素必须同步添加
                    'time': [ img_info['index'] ],           # 当前帧索引，后期将改为时间
                    'bboxs': [[ int(obj['bbox'][0]),         # bboxs框
                                int(obj['bbox'][1]),
                                int(obj['bbox'][2]),
                                int(obj['bbox'][3]),]],                                  
                    'centre': [ get_centre(obj['bbox']) ],   # 中心位置
                    'speed': [None],                         # 当前帧速度
                    'classes': [int(obj['cls_pred'])],       # 当前帧对应类别,后期会选择多数类别代替之
                }
            else:   # 由于是否为起始帧对后期处理方式有差异，于是采用if-else结构
                # 速度计算：
                t_centre = get_centre(obj['bbox'])
                sx = (t_centre[0] - self.tPaths[t_id]['centre'][-1][0])/(img_info['index']-self.tPaths[t_id]['time'][-1])
                sy = (t_centre[1] - self.tPaths[t_id]['centre'][-1][1])/(img_info['index']-self.tPaths[t_id]['time'][-1])

                self.tPaths[t_id]['time'].append(img_info['index'])
                self.tPaths[t_id]['bboxs'].append( [
                            int(obj['bbox'][0]),
                            int(obj['bbox'][1]),
                            int(obj['bbox'][2]),
                            int(obj['bbox'][3]),
                        ])
                self.tPaths[t_id]['centre'].append(t_centre)
                self.tPaths[t_id]['speed'].append([sx, sy])
                self.tPaths[t_id]['classes'].append(int(obj['cls_pred']))
                self.avgBbox = (self.avgBbox + getAvgBbox(obj['bbox']))/2
                # 判断当前速度是否优质：
                if vLen([sx,sy]) > self.speedTh and int(obj['cls_pred']) in self.classFilter:
                    self.highGradeSpeed.append([getDirection([sx, sy])])

        # 处理在当前帧中结束的id:
        endPaths = []
        for i in img_info['del_id']:
            if i in self.tPaths.keys():     # 看id是否在tPaths中
                endPaths.append(self.tPaths[i])
                # 如果长度符合阈值要求，则将之保存如highGradePaths
                if len(self.tPaths[i]['centre']) >= self.pathLTh:
                    self.saveToHighGradePaths(self.tPaths[i])
                    print('id为' + str(i) + '已被结算')
                self.tPaths.pop(i)
        return endPaths

    def saveToHighGradePaths(self, path):
        path['classes'] = stats.mode(path['classes'])[0][0]     # 获得classes中的众数作为物体的类别
        if path['classes'] in self.classFilter:
            self.highGradePaths.append(path)
        
    def MapGeneration(self):
        print('数据统计完毕，开始行为分析')
        # 计算主辅轴：
        print('正在进行方向聚类')
        k = KMeans(n_clusters=2)
        k.fit(self.highGradeSpeed)
        axis1 = k.cluster_centers_[0][0]
        axis2 = k.cluster_centers_[1][0]
        mainAxis = axis1 if abs(axis1) > abs(axis2) else axis2
        secondaryAxis = axis1 if abs(axis1) < abs(axis2) else axis2
        print('方向聚类结果如下：')
        print('主轴方向：' + str(mainAxis))
        print('辅轴方向：' + str(secondaryAxis))
        print('正在生成速度地图')
        self.sMap = speedMap(
            mainAxis=mainAxis, 
            secondaryAxis=secondaryAxis,
            avgBbox=self.avgBbox,
        )
        # 速度图统计：
        i = 0
        for path in self.highGradePaths:
            self.sMap.update(path)
            i += 1
            print('数据处理进度:' + str(i) + '/' + str(len(self.highGradePaths)))
        print('速度图生成完毕！')
        mainMask = self.sMap.getMainMask()
        cv2.imwrite(self.mainMapSavePath, mainMask)
        print('关键区域蒙版已经存储为' + self.mainMapSavePath)
        stopMask = self.sMap.getStopMask()
        cv2.imwrite(self.stopMapSavePath, stopMask)
        print('停止区域蒙版已经存储为' + self.stopMapSavePath)
        eM = eModel(sMap=self.sMap,paths=self.highGradePaths)
        eM.save(self.modelName)
            



    def process(self, **kwargs):
        imgs_info = kwargs['imgs_info']
        for img_info in imgs_info:
            self.img_info2Path(img_info)
            print(str(img_info['index']) + ':数据收集进度：speedLen:' + str(len(self.highGradeSpeed)) + '/' + str(self.minDataSize) + '   pathsLen:' + str(len(self.highGradePaths)))
        if len(self.highGradeSpeed) > self.minDataSize:
            self.MapGeneration()
        return kwargs