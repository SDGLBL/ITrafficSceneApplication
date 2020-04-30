from components.registry import HEAD
from .base import BaseVideoPipeline
import mmcv


@HEAD.register_module
class VideoFilePipeline(BaseVideoPipeline,mmcv.VideoReader):

    def __init__(self, filename,step, cache_capacity=10):
        self.step = step
        super().__init__(filename, cache_capacity)

    def __iter__(self):
        return super().__iter__()

    def __next__(self):
        return super().__next__()

    def __next__(self):
        imgs = []
        for _ in range(self.step):
            img = self.read()
            if img is not None:
                imgs.append(img)
            else:
                return StopIteration
        return img

    def __len__(self):
        return super().__len__()

    def __getitem__(self, index):
        return super().__getitem__(index)

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)

    def __enter__(self):
        return super().__enter__()

    def get_shape(self):
        return (int(self.height),int(self.width),3)

    def get_fps(self):
        return self.fps




