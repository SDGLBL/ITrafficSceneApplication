import mmcv

from utils.dao import get_current_time
from .base import BaseVideoPipeline
from .registry import HEAD


@HEAD.register_module
class VideoFileHead(mmcv.VideoReader, BaseVideoPipeline):
    def __init__(self, filename, step, cache_capacity=10):
        """
        文件视频读取Head
        Args:
            filename: 视频文件路径
            step: 一次读取多少张图片
            cache_capacity: 缓冲区大小
        """
        if step % 2 != 0 and step != 1:
            raise AttributeError('步长必须为2的倍数')
        self.step = step
        self.start_index = 0
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
                imgs_info.append({
                    'time':get_current_time(), # 使用的时间
                    'index':self.start_index, # 对应视频中的第几帧
                    'shape':img.shape # 图像的shape (H,W,C)
                    })
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




