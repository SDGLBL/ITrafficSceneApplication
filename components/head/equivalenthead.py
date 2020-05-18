import json

import mmcv

from .base import BaseVideoPipeline
from .registry import HEAD


@HEAD.register_module
class EquivalentHead(mmcv.VideoReader, BaseVideoPipeline):
    def __init__(self, filename, json_filename, step, cache_capacity=10):
        """
        虚拟数据读取头
        通过读取已经生成的json和视频文件伪造出神经网络运行的效果，以给其他开发人员进行调试使用
        Args:
            filename: 视频路径
            json_filename: json数据路径
            step: 一次读取几张图片
            cache_capacity: 缓存区大小
        """
        if step % 2 != 0 and step != 1:
            raise AttributeError('步长必须为2的倍数')
        self.step = step
        self.start_index = 0
        self.json_filename = json_filename
        self.json_file_read = open(json_filename, 'r', encoding="utf-8")
        super().__init__(filename, cache_capacity)

    def __iter__(self):
        return super().__iter__()

    def __next__(self):
        """迭代器返回imgs和imgs_info

        Raises:
            StopIteration: 如果不能满足batch_size则停止迭代

        Returns:
            tuple(imgs,imgs_info): imgs是图像list，imgs_info则是每张图像的必需信息
        """        
        imgs = []
        imgs_info = []
        for _ in range(self.step):
            img = self.read()
            if img is not None:
                imgs.append(img)
                json_str = self.json_file_read.readline()
                imgs_info.append(json.loads(json_str))
                self.start_index += 1
            else:
                raise StopIteration
        return {'imgs': imgs, 'imgs_info': imgs_info}

    def __getitem__(self, index):
        return super().__getitem__(index)

    def __len__(self):
        return super().__len__()

    def get_shape(self):
        return (int(self.height),int(self.width),3)

    def get_fps(self):
        return self.fps