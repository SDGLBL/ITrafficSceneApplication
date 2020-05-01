from .registry import HEAD
from .base import BaseVideoPipeline
import mmcv


@HEAD.register_module
class VideoFileHead(mmcv.VideoReader, BaseVideoPipeline):

    def __init__(self, filename,step, cache_capacity=10):
        self.step = step
        super().__init__(filename, cache_capacity)

    def __iter__(self):
        return super().__iter__()

    def __next__(self):
        imgs = []
        for _ in range(self.step):
            img = self.read()
            if img is not None:
                imgs.append(img)
            else:
                return StopIteration
        return imgs

    def __getitem__(self, index):
        return super().__getitem__(index)


    def get_shape(self):
        return (int(self.height),int(self.width),3)

    def get_fps(self):
        return self.fps




