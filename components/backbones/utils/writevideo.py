import cv2
from cv2 import VideoWriter_fourcc
from components.backbones.registry import BACKBONE_COMPONENT
from components.backbones.base import BaseBackboneComponent

@BACKBONE_COMPONENT.register_module
class WriteVideoComponent(BaseBackboneComponent):
    def __init__(self,resolution,fps,fourcc='avc1',write_path='./save.mp4'):
        super().__init__()
        self.vwriter = cv2.VideoWriter(
            write_path,
            VideoWriter_fourcc(*fourcc),
            fps,
            resolution
        )

    def process(self, **kwargs):
        super().process(**kwargs)
        imgs = kwargs['imgs']
        for img in imgs:
            self.vwriter.write(img)
        return kwargs
