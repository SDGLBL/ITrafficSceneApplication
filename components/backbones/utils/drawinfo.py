from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont


@BACKBONE_COMPONENT.register_module
class DrawInfoComponent(BaseBackboneComponent):
    def __init__(self, size=(1080,1920), bgPath='bg.png'):
        super().__init__()
        self.size = (1080,1920)
        self.info = {
            'pass_count_table': None,
            'broadcast': []
        }
        self.maxLenBroadcast = 13
        self.infoID = 1
        self.plate = None
        self.change = False
        self.bg = cv2.imread(bgPath)
        self.transformInfo = {
            '直行': 'go straight',
            '左拐': 'turn right',
            '右拐': 'turn left'
        }
        self.updata()

    def addInfoPlate(self, img):
        newImg = np.concatenate((img, self.plate), axis=1)
        return newImg


    def updata(self, img_info=None):
        if img_info is None:
            data = np.empty((4,4), dtype=str)
            data = [
                [' ', '左拐', '直行', '右拐', '总计'],
                ['car', 0, 0, 0, 0],
                ['bus', 0, 0, 0, 0],
                ['truck', 0, 0, 0, 0],
                ['总计', 0, 0, 0, 0]
            ]
            self.info['pass_count_table'] = data
            self.change = True
            self.plate = self.makePlate()
        else:
            for analysis in img_info['analysis']:
                if analysis['info_type'] == 'pass':
                    info_str = '{}>A {} passed and {}'.format(self.infoID, analysis['obj_type'], self.transformInfo[analysis['passage_type']])
                    self.infoID += 1
                    # print(info_str)
                    self.info['broadcast'].append(info_str)
                    self.change = True

            if 'pass_count_table' in img_info.keys():
                if info['pass_count_table'][1]:
                    self.info['pass_count_table'] = img_info['pass_count_table'][0]
                    self.change = True
            self.plate = self.makePlate()
        return 0

    def makePlate(self):
        if not self.change:
            return self.plate
        plate = np.array(self.bg)
        # 绘制车流量表
        start = [165,205]
        step = [120, 50]
        table = self.info['pass_count_table']
        table = np.array(table)
        table = table[1:, 1:]

        for i in range(len(table)):
            for j in range(len(table[i])):
                cv2.putText(plate,
                            str(int(float(table[i][j]))),
                            (start[0]+step[0]*j, start[1]+step[1]*i),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0),1)

        # 绘制播报信息：
        start = [13,480]
        step = [0,47]
        listLen = 0
        broadcast = self.info['broadcast']
        for i in range(len(broadcast)-1, -1, -1):
            # print(self.info['broadcast'][i])
            cv2.putText(plate,
                        self.info['broadcast'][i],
                        (start[0], start[1] + step[1] * listLen),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            listLen += 1
            if listLen > self.maxLenBroadcast:
                break

        # 适应图片大小
        h = int(self.size[0])
        w = int(plate.shape[1] * self.size[0]/plate.shape[0])
        plate = cv2.resize(plate, (w, h))
        self.change = False
        return plate


    def process(self, **kwargs):
        # super().process(**kwargs)
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        for img, img_info in zip(imgs, imgs_info):
            self.updata(img_info)
            imgPlate = self.addInfoPlate(img)
            img_info['show_img'] = imgPlate
        return kwargs 