from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT
from utils.modeltools import *
import numpy as np

@BACKBONE_COMPONENT.register_module
class TrafficStatistics(BaseBackboneComponent):
    def __init__(self, eModelPath,is_process=False):
        self.model=emdLoad(eModelPath)
        # 区分左拐右拐直行：
        self.dirK = self.model['dir_classifier']
        self.dirStr = {}
        if self.model['reachable_mat'].shape[1] == 3:
            self.indX = ['左拐','右拐','直行']
            nc = np.array(self.dirK.cluster_centers_)
            nc = nc[:,0]
            dirC = np.argsort(nc)
            self.dirStr[dirC[0]] = self.indX[0]
            self.dirStr[dirC[1]] = self.indX[1]
            self.dirStr[dirC[2]] = self.indX[2]
            print(self.dirStr)
        elif self.model['reachable_mat'].shape[1] == 2:
            self.indX = ['左拐','右拐']
            dirC = np.argsort(self.dirK.cluster_centers_)
            self.dirStr[dirC[0]] = self.indX[0]
            self.dirStr[dirC[1]] = self.indX[1]
        self.laneStr = {}
        nc = np.array(self.model['lane_classifier'].cluster_centers_)
        nc = nc[:,0]
        laneC = np.argsort(nc)
        k = 1
        for i in laneC:
            self.laneStr[i] = '第{}车道'.format(str(str(k)))
            k += 1
        self.indY = ['car', 'truck', 'bus']
        self.indX = np.array(self.indX)
        self.indY = np.array(self.indY)
        self.pass_count_table = np.zeros((len(self.indY), len(self.indX)))
        self.is_process = is_process
            
    def pathStatistics(self, img, img_info):
        img_info['analysis'] = []
        legalTurn = True
        for path in img_info['end_path']:
            if isPass(path, self.model):
                laneAndDir = pathsStatus(path, self.model)
                id = str(path['id'])
                cls_name = path['cls_name']
                number_plate = path['number_plate']
                if laneAndDir is None:
                    # print('路劲太短无法识别方向')
                    dir = None
                    lane = None
                else:
                    dir = self.dirStr[laneAndDir[1]]
                    lane = self.laneStr[laneAndDir[0]]
                    legalTurn = self.model['reachable_mat'][laneAndDir[0], laneAndDir[1]]
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
                # print(passInfo)
                img_info['analysis'].append(passInfo)
                if not legalTurn:
                    foulInfo = {
                        'info_type': 'illegal_turn',
                        'id': id,
                        'start_time': path['start_time'],
                        'end_time': path['end_time'],
                        'passage_type': dir,
                        'obj_type': cls_name,
                        'number_plate': number_plate,
                    }
                    img_info['analysis'].append(foulInfo)
                self.pass_count_table[self.indY==cls_name, self.indX==dir] += 1
                # print(self.pass_count_table)
        img_info['pass_count_table'] = self.getTabele(self.indX, self.indY, self.pass_count_table)
                

        
    def getTabele(self,indX, indY, data):
        # 计算总和：
        sum0 = np.sum(data, axis=0)
        sum1 = np.sum(data, axis=1)
        sum0 = sum0[np.newaxis, :]
        table = np.concatenate((data, sum0), axis=0)
        sum1 = np.append(sum1, np.sum(sum1))
        sum1 = sum1[:, np.newaxis]
        table = np.concatenate((table, sum1), axis=1)
        # 添加表头
        indX = np.append(indX,['总和'])
        indX = indX[np.newaxis, :]
        table = np.concatenate((indX, table), axis=0)
        indY = np.append(indY,['总和'])
        indY = np.append([' '], indY)
        indY = indY[:, np.newaxis]
        table = np.concatenate((indY,table), axis=1)
        # print(table)
        return table.tolist()


    def process(self, **kwargs):
        if not self.is_process:
            return kwargs
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        for img, img_info in zip(imgs, imgs_info):
            self.pathStatistics(img, img_info)
        return kwargs

            

