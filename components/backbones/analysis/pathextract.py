import utils.analysistools as utils
from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT

@BACKBONE_COMPONENT.register_module
class PathExtract(BaseBackboneComponent):
    def __init__(self):
        self.tPaths = {}
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
                    'state': 0
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
    def __init__(self):
        pass

    def __call__(self, object):
        return True