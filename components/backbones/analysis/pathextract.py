import utils.analysistools as utils
from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT
from utils.modeltools import *
from utils.utils import identify_number_plate

@BACKBONE_COMPONENT.register_module
class PathExtract(BaseBackboneComponent):
    def __init__(self, eModelPath=None, isPlate=False):
        self.tPaths = {}
        if eModelPath is not None:
            self.model=emdLoad(eModelPath)
            self.registerConstraint = Constraint(self.model)
        else:
            self.model=None
            self.registerConstraint = Constraint()


    def tPathsManagement(self, img, img_info):
        img_info['end_path'] = []
        # 处理当前存在的目标
        for object in img_info['objects']:
            id = object['id']
            centre = utils.getCentre(object['bbox'])
            # 初始化第一次出现的目标
            if id not in self.tPaths.keys() and self.registerConstraint(object):
                self.tPaths[id] = {
                    'id': id,
                    'start_time': img_info['time'],
                    'end_time': None,
                    'bboxs': [object['bbox']],
                    'indexs': [img_info['index']],
                    'dots': [centre],
                    'number_plate': None,
                    'maybe_classes': {object['cls_pred']: 1},
                    'state': img_info['index']
                }
            # 完善正在运动的目标：
            elif id in self.tPaths.keys():
                state = self.getState(centre)
                tPath = self.tPaths[id]
                tPath['bboxs'].append(object['bbox'])
                tPath['indexs'].append(img_info['index'])
                tPath['dots'].append(centre)
                if object['cls_pred'] not in tPath['maybe_classes'].keys():
                    tPath['maybe_classes'][object['cls_pred']] = 0
                tPath['maybe_classes'][object['cls_pred']] += 1

                # 在模型存在时，进行车牌识别等操作：
                if self.model is not None:
                    if tPath['number_plate'] is None and img_info['index']-tPath['state']>=5:
                        tPath['state'] = img_info['index']
                        number_plate = identify_number_plate(img, object['bbox'])
                        if number_plate is not None:
                            tPath['number_plate'] = number_plate

        # 结算已经跟踪结束的目标：
        for del_id in img_info['del_id']:
            if del_id in self.tPaths.keys():
                tPath = self.tPaths[del_id]
                tPath['end_time'] = img_info['time']
                tPath['cls_name'] = max(tPath['maybe_classes'], key=tPath['maybe_classes'].get)
                del tPath['maybe_classes']
                img_info['end_path'].append(tPath)
                self.tPaths.pop(del_id)
        return img, img_info

    def getState(self, centre):
        return 0

    def process(self, **kwargs):
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        for img, img_info in zip(imgs, imgs_info):
            self.tPathsManagement(img, img_info)
        return kwargs


class Constraint:
    def __init__(self, model=None):
        self.startArea = None
        self.half = None
        self.classes = None
        self.model = None
        if model is not None:
            self.model = model
            if model['type'] == 'crossroad':
                self.startArea = utils.getMapMask(self.model['main_map'], th=0.2)
                self.half = -1
                self.classes = ['car', 'trucker', 'bus'] 

    def __call__(self, object):
        cls_pred = object['cls_pred']
        centre = utils.getCentre(object['bbox'])
        if self.startArea is not None:
            if not self.startArea[centre[1], centre[0]]:
                return False
        if self.half is not None:
            if dotStatus(centre, self.model) != self.half:
                return None
        if self.classes is not None:
            if cls_pred not in self.classes:
                return False
        return True

