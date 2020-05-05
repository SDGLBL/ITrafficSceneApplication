import cv2
from cv2 import VideoWriter_fourcc

from components.backbones.base import BaseBackboneComponent
from components.backbones.registry import BACKBONE_COMPONENT


@BACKBONE_COMPONENT.register_module
class WriteVideoComponent(BaseBackboneComponent):
    def __init__(self, resolution, fps, fourcc='avc1', write_path='./save.mp4'):
        super().__init__()
        self.vwriter = cv2.VideoWriter(
            write_path,
            VideoWriter_fourcc(*fourcc),
            fps,
            resolution
        )
        self.resolution = resolution

    def process(self, **kwargs):
        super().process(**kwargs)
        imgs = kwargs['imgs']
        for img in imgs:
            if not (img.shape[1], img.shape[0]) == self.resolution:
                img = cv2.resize(img, self.resolution)
            self.vwriter.write(img)
        return kwargs
