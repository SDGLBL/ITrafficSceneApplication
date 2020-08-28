from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT
from utils.modeltools import *
import numpy as np

@BACKBONE_COMPONENT.register_module
class TrafficStatisticsByStraight(BaseBackboneComponent):
    """
        用于直行道的车辆计数类
    """
    def __init__(self, is_process=False, direction=["to", "from"], passLine = 540):
        """初始化函数
        Args:
            is_process (bool, optional): 是否开启该模块. Defaults to False.
            direction (str, optional): 表示计数方向，['to']表示只统计去向的车. ["to", "from"]表示即统计来向也统计去向的车，Defaults to ["to", 'from'].
            passLine (int, optional): 表示通过该线则计数器加一。 Defaults to 720.
        """
        # 表格初始化：
        self.indX = np.array(direction)    # 只有直行一个方向
        self.indY = np.array(['car', 'truck', 'bus','motorbike'] )     # 统计三个类别的车辆
        self.pass_count_table = np.zeros((len(self.indY), len(self.indX)))
        self.is_process = is_process
        self.passLine = passLine
        self.trans = {
            'car':'小汽车',
            'bus':'巴士',
            'truck':'卡车',
            'motorbike':'摩托车',
            'to':'驶去',
            'from':'驶来'
        }
        self.CIndX = np.array(self.indX)
        for i in range(len(self.CIndX)):
            if self.CIndX[i] in self.trans:
                self.CIndX[i] = self.trans[self.CIndX[i]]
        self.CIndY = np.array(self.indY)
        for i in range(len(self.CIndY)):
            if self.CIndY[i] in self.trans:
                self.CIndY[i] = self.trans[self.CIndY[i]]
            
    def pathStatistics(self, img, img_info):
        img_info['analysis'] = []
        change = False
        # 遍历img_info中的每条路劲
        for path in img_info['end_path']:
            # print(path['id'])
            id = str(path['id'])
            cls_name = path['cls_name']
            # 如果这条路径符合方向和位置要求，则对该条路劲进行处理：
            d = self.isPass(path)
            if d is not None and d in self.indX and (cls_name in self.indY):
                change = True;
                # print(self.indY == cls_name)
                # print(self.pass_count_table[self.indY == cls_name][self.indX == d])
                self.pass_count_table[self.indY == cls_name, self.indX == d] += 1
                passInfo = {
                    'info_type': 'pass',
                    'id': id,
                    'start_time': path['start_time'],
                    'end_time': path['end_time'],
                    'passage_type': d,
                    'obj_type': cls_name,
                    'number_plate': None
                }
                print("一辆车通过")
                print(passInfo)
                img_info['analysis'].append(passInfo)
        img_info['pass_count_table'] = [self.getTabele(self.CIndX, self.CIndY, self.pass_count_table), change]  

        
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
        indY = np.append(['车辆类型'], indY)
        indY = indY[:, np.newaxis]
        table = np.concatenate((indY,table), axis=1)
        # print(table)
        return table.tolist()

    def isPass(self, path):
        """判断一条路径的通过状态

        Args:
            path (dict): 传入路径

        Returns:
            str: 返回 “to” 表示去向路径，返回 “from” 表示来向路径，返回 None 表示该路径未通过。
        """
        dots = path['dots']
        start = dots[0][1]
        end = dots[-1][1]
        if start < self.passLine < end:
            return 'from'
        elif start > self.passLine > end:
            return 'to'
        return None



    def process(self, **kwargs):
        if not self.is_process:
            return kwargs
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        for img, img_info in zip(imgs, imgs_info):
            self.pathStatistics(img, img_info)
        return kwargs
