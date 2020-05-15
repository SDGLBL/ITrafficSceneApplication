from .eModel import eModel
from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT
from .tools import get_centre

@BACKBONE_COMPONENT.register_module
class stateAnalysis(BaseBackboneComponent):
    def __init__(self, eModelPath):
        eM = eModel.load(eModelPath)
        self.mainMask = eM.sMap.getMainMask()
        self.stopLine = eM.sMap.getStopLine()
        self.avgBbox = eM.sMap.avgBbox
        self.classes = [2]
        self.objDict = {}
        self.passCount = 0

    def dotByStopLine(self, dot:list):
        k, b = self.stopLine
        print( '#' + str(self.avgBbox/4) + '#' + str(k) + '#' + str(b) + '#' + str(k*dot[0] + b - dot[1]))
        if k*dot[0] + b - dot[1] > self.avgBbox/4:
            return 1
        elif k*dot[0] + b - dot[1] < -self.avgBbox/4:
            return -1
        else:
            return 0

        
    def dotInMainMask(self, dot:list):
        return self.mainMask[int(dot[1]), int(dot[0])] != 0


    def analysis(self, img_info):
        objs = img_info['objects']
        # 新目标添加统计
        for obj in objs:
            if int(obj['cls_pred']) not in self.classes:
                continue
            id = obj['id']
            centre = get_centre(obj['bbox'])
            if id not in self.objDict.keys() and self.dotInMainMask(centre):
                print(str(img_info['index']) + '找到一个自关键区域发出的车辆，id为' + str(id))
                self.objDict[id] = {
                    'id':id,
                    'startDot': centre,
                    # 一下两项必须同步添加
                    'path': [centre],
                    'time': [img_info['index']],
                    'passState': self.dotByStopLine(centre)
                }
            elif id in self.objDict.keys():
                passState = self.dotByStopLine(centre)
                lastPassState = self.objDict[id]['passState']
                if passState == 0 or passState==lastPassState:
                    pass
                else:
                    self.objDict[id]['passState'] = passState
                    print('ID为：' + id + '的车辆过线，计数器加一')
                    self.passCount += 1
                self.objDict[id]['path'].append(centre)
                self.objDict[id]['time'].append(img_info['index'])

        
        img_info['passCount'] = self.passCount


    def process(self, **kwargs):
        imgs_info = kwargs['imgs_info']
        for img_info in imgs_info:
            #print('正在处理第'+ str(img_info['index']) + '张图片：')
            self.analysis(img_info) 
        return kwargs