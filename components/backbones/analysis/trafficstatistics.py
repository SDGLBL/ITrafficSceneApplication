from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT
from utils.modeltools import *
import numpy as np

@BACKBONE_COMPONENT.register_module
class TrafficStatistics(BaseBackboneComponent):
    def __init__(self, eModelPath):
        self.model=emdLoad(eModelPath)
        # 区分左拐右拐直行：
        self.dirK = self.model['dir_classifier']
        self.dirStr = {}
        self.pass_count = 0
        self.left_pass_count = 0
        self.right_pass_count = 0
        self.straight_pass_count = 0
        self.none_dir_pass_count = 0
        self.car_pass_count = 0
        self.truck_pass_count = 0
        self.bus_pass_count = 0
        if self.model['reachable_mat'].shape[1] == 3:
            nc = np.array(self.dirK.cluster_centers_)
            nc = nc[:,0]
            dirC = np.argsort(nc)
            self.dirStr[dirC[0]] = '左拐' 
            self.dirStr[dirC[1]] = '直行'
            self.dirStr[dirC[2]] = '右拐'
            print(self.dirStr)
        elif self.model['reachable_mat'].shape[1] == 2:
            dirC = np.argsort(self.dirK.cluster_centers_)
            self.dirStr[dirC[0]] = '左拐' 
            self.dirStr[dirC[1]] = '右拐'
        self.laneStr = {}
        nc = np.array(self.model['lane_classifier'].cluster_centers_)
        nc = nc[:,0]
        laneC = np.argsort(nc)
        k = 1
        for i in laneC:
            self.laneStr[i] = '第{}车道'.format(str(str(k)))
            k += 1
            
    def pathStatistics(self, img, img_info):
        img_info['analysis'] = []
        for path in img_info['end_path']:
            if isPass(path, self.model):
                self.pass_count += 1
                laneAndDir = pathsStatus(path, self.model)
                id = str(path['id'])
                cls_name = path['cls_name']
                number_plate = path['number_plate']
                if laneAndDir is None:
                    print('路劲太短无法识别')
                    dir = None
                    lane = None
                else:
                    dir = self.dirStr[laneAndDir[1]]
                    lane = self.laneStr[laneAndDir[0]]
                    print( 'id:{}为的{}，车牌为{},自第{}发出,{}'.format(id, cls_name, number_plate, lane, dir) )
                passInfo = {
                    'info_type': 'pass',
                    'id': id,
                    'start_time': path['start_time'],
                    'end_time': path['end_time'],
                    'passage_type': dir,
                    'obj_type': cls_name,
                    'number_plate': number_plate
                }
                print(passInfo)
                img_info['analysis'].append(passInfo)

                # 车辆类别统计
                if cls_name == 'car':
                    self.car_pass_count += 1
                elif cls_name == 'truck':
                    self.truck_pass_count += 1
                elif cls_name == 'bus':
                    self.bus_pass_count += 1
                
                # 方向统计
                if dir is None:
                    self.none_dir_pass_count += 1
                elif dir == '左拐':
                    self.left_pass_count += 1
                elif dir == '直行':
                    self.straight_pass_count += 1
                elif dir == '右拐':
                    self.right_pass_count += 1 
                print('a:{},c{},t{},b{},n{},l{},s{},r{}'.format(
                    str(self.pass_count),
                    str(self.car_pass_count),
                    str(self.truck_pass_count),
                    str(self.bus_pass_count),
                    str(self.none_dir_pass_count),
                    str(self.left_pass_count),
                    str(self.straight_pass_count),
                    str(self.right_pass_count)
                ))

        img_info['pass_count'] = self.pass_count
        img_info['car_pass_count'] = self.car_pass_count
        img_info['truck_pass_count'] = self.truck_pass_count
        img_info['bus_pass_count'] = self.bus_pass_count
        img_info['none_dir_pass_count'] = self.none_dir_pass_count
        img_info['left_pass_count'] = self.left_pass_count
        img_info['straight_pass_count'] = self.straight_pass_count
        img_info['right_pass_count'] = self.right_pass_count




    def process(self, **kwargs):
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        for img, img_info in zip(imgs, imgs_info):
            self.pathStatistics(img, img_info)
        return kwargs

            

