from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont


@BACKBONE_COMPONENT.register_module
class DrawInfoComponent(BaseBackboneComponent):
    def __init__(self, size=(1080,1920), bgPath='bg.png'):
        super().__init__()
        self.drwa_info = []
        self.size = size
        self.info = {}
        self.plate = None
        self.bg = cv2.imread(bgPath)
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
            self.plate = self.makePlate()
        else:
            if 'pass_count_table' in img_info.keys():
                self.info['pass_count_table'] = img_info['pass_count_table']
                self.plate = self.makePlate()
        return 0

    def makePlate(self):
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

        h = int(self.size[0])
        w = int(plate.shape[1] * self.size[0]/plate.shape[0])
        plate = cv2.resize(plate, (w, h))
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