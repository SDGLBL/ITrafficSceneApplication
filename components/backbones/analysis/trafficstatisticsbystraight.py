from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT
from utils.modeltools import *
import numpy as np

@BACKBONE_COMPONENT.register_module
class TrafficStatisticsByStraight(BaseBackboneComponent):
    """
        用于直行道的车辆计数类
    """
    def __init__(self, is_process=False, direction="to", passLine = 720):
        """初始化函数
        Args:
            is_process (bool, optional): 是否开启该模块. Defaults to False.
            direction (str, optional): 选择统计方向，默认是去向方向"to"，将之设定为 "from" 表示统计来向车辆. Defaults to "to".
            passLine (int, optional): 表示通过该线则计数器加一。 Defaults to 720.
        """
        # 表格初始化：
        self.indX = ['直行']    # 只有直行一个方向
        self.indY = ['car', 'truck', 'bus']     # 统计三个类别的车辆
        self.pass_count_table = np.zeros((len(self.indY), len(self.indX)))
        self.is_process = is_process
        self.direction = direction
        self.passLine = passLine
            
    def pathStatistics(self, img, img_info):
        img_info['analysis'] = []
        change = False
        # 遍历img_info中的每条路劲
        for path in img_info['end_path']:
            id = str(path['id'])
            cls_name = path['cls_name']
            # 如果这条路径符合方向和位置要求，则对该条路劲进行处理：
            d = self.isPass(path)
            if d is not None and d==self.direction and (cls_name in self.indX):
                change = True;
                if cls_name == 'car':
                    self.pass_count_table[0] += 1
                else if cls_name = 'truck':
                    self.pass_count_table[1] += 1
                else if cls_name = 'bus':
                    self.pass_count_table[2] += 1
                passInfo = {
                    'info_type': 'pass',
                    'id': id,
                    'start_time': path['start_time'],
                    'end_time': path['end_time'],
                    'passage_type': '直行',
                    'obj_type': cls_name,
                    'number_plate': None
                }
                img_info['analysis'].append(passInfo)


        img_info['pass_count_table'] = [self.getTabele(self.indX, self.indY, self.pass_count_table), change]
                

        
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
            return False
        else if start > self.passLine > end:
            return True
        return None



    def process(self, **kwargs):
        if not self.is_process:
            return kwargs
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        for img, img_info in zip(imgs, imgs_info):
            self.pathStatistics(img, img_info)
        return kwargs
